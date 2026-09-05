from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import secrets
import smtplib
import ssl
import string
import threading
import time
import uuid
import zipfile
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from typing import Any, AsyncGenerator, Literal
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends, FastAPI, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{ROOT / 'cloud-data.sqlite3'}")
APP_SECRET = os.environ.get("APP_SECRET", "")
try:
    APP_VERSION = str(json.loads((ROOT / "version.json").read_text(encoding="utf-8"))["version"])
except (OSError, ValueError, KeyError, TypeError):
    APP_VERSION = "3.2.0"


def environment_port(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
        return value if 1 <= value <= 65535 else default
    except ValueError:
        return default


DEPLOYMENT_HTTP_PORT = environment_port("PUBLIC_HTTP_PORT", 80)
DEPLOYMENT_HTTPS_PORT = environment_port("PUBLIC_HTTPS_PORT", 443)
DEPLOYMENT_APP_PORT = environment_port("PUBLIC_APP_PORT", 8088)
DEPLOYMENT_BIND_ADDRESS = os.environ.get("PUBLIC_APP_BIND_ADDRESS", "127.0.0.1")
DEPLOYMENT_PROXY_MODE = "external" if os.environ.get("PUBLIC_PROXY_MODE") == "external" else "bundled"
PORT_CONTROL_DIR = Path(os.environ["PORT_CONTROL_DIR"]).resolve() if os.environ.get("PORT_CONTROL_DIR") else None
SESSION_COOKIE = "q400_session"
MAX_STATE_BYTES = 8 * 1024 * 1024
MAX_UPDATE_BYTES = 96 * 1024 * 1024
MAX_LOGO_BYTES = 1024 * 1024
MAX_AVATAR_BYTES = 1024 * 1024
DEFAULT_AVATAR_BYTES = base64.b64decode((ROOT / "cloud" / "assets" / "default-avatar.b64").read_text(encoding="ascii").strip(), validate=True)
UPDATE_REPOSITORY = os.environ.get("UPDATE_REPOSITORY", "Den901/quiz-400-vvf-2026").strip()
UPDATE_ASSET_NAME = os.environ.get("UPDATE_ASSET_NAME", "Quiz-400-VVF-2026-Server.zip").strip()
USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,39}$")
DUCKDNS_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.duckdns\.org)?$")
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$")
CHALLENGE_SECONDS = 40 * 60
CHALLENGE_TIMEZONE = ZoneInfo("Europe/Rome")
CHALLENGE_LOGIC_TOPICS = ("deduzioni", "serie", "verbale", "calcolo", "figure", "insiemi", "relazioni", "ordinamenti", "brani", "mista")
CHALLENGE_SELECTABLE_LOGIC_TOPICS = tuple(topic for topic in CHALLENGE_LOGIC_TOPICS if topic != "brani")

if not APP_SECRET:
    if os.environ.get("Q400_ENV", "development") == "production":
        raise RuntimeError("APP_SECRET deve essere configurato in produzione.")
    APP_SECRET = "development-only-change-me"


def utcnow() -> datetime:
    return datetime.now(UTC)


def encryption_key() -> bytes:
    digest = hashlib.sha256(APP_SECRET.encode("utf-8")).digest()
    import base64

    return base64.urlsafe_b64encode(digest)


fernet = Fernet(encryption_key())
password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
DUMMY_PASSWORD_HASH = password_hasher.hash("dummy-password-never-used")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(254), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(10), default="user", index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    privacy_policy_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    privacy_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    state: Mapped["UserState"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    avatar: Mapped["UserAvatar | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    sessions: Mapped[list["LoginSession"]] = relationship(cascade="all, delete-orphan")
    reset_tokens: Mapped[list["PasswordReset"]] = relationship(cascade="all, delete-orphan")


class UserAvatar(Base):
    __tablename__ = "user_avatars"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    data: Mapped[str] = mapped_column(Text)
    mime: Mapped[str] = mapped_column(String(20))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user: Mapped[User] = relationship(back_populates="avatar")


class UserState(Base):
    __tablename__ = "user_states"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user: Mapped[User] = relationship(back_populates="state")


class LoginSession(Base):
    __tablename__ = "login_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(String(300), default="")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    target_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    challenge_date: Mapped[date] = mapped_column(Date, primary_key=True)
    question_ids: Mapped[list[str]] = mapped_column(JSON)
    composition: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    app_version: Mapped[str] = mapped_column(String(40), default=APP_VERSION)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DailyChallengeAttempt(Base):
    __tablename__ = "daily_challenge_attempts"
    __table_args__ = (UniqueConstraint("challenge_date", "user_id", name="uq_daily_challenge_attempt_user_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_date: Mapped[date] = mapped_column(ForeignKey("daily_challenges.challenge_date", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    answers: Mapped[list[int | None]] = mapped_column(JSON, default=list)
    question_seconds: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_x100: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class QuestionReport(Base):
    __tablename__ = "question_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reason: Mapped[str] = mapped_column(String(40))
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class QuestionRating(Base):
    __tablename__ = "question_ratings"
    __table_args__ = (UniqueConstraint("question_id", "user_id", name="uq_question_rating_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DisabledQuestion(Base):
    __tablename__ = "disabled_questions"

    question_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    disabled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    disabled_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


engine_options: dict[str, Any] = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # Keep enough headroom for concurrent PWA API calls (including leaderboard
    # avatars). Dependency cleanup runs on the event loop below, so a saturated
    # worker pool cannot strand checked-out database connections.
    engine_options.update({"pool_size": 20, "max_overflow": 20, "pool_timeout": 10, "pool_recycle": 1800})
engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


DEFAULT_SETTINGS: dict[str, Any] = {
    "site_name": "Quiz 400 VVF 2026",
    "registration_enabled": True,
    "daily_challenge_enabled": True,
    "daily_challenge_required": False,
    "theoretical_cutoff": 14.71,
    "public_url": "",
    "session_days": 30,
    "reset_token_minutes": 30,
    "duckdns_enabled": False,
    "duckdns_domain": "",
    "duckdns_token": "",
    "duckdns_interval_minutes": 5,
    "duckdns_last_status": {},
    "smtp_enabled": False,
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_password": "",
    "smtp_from_email": "",
    "smtp_use_tls": True,
    "smtp_last_status": {},
    "brand_logo_data": "",
    "brand_logo_mime": "",
    "brand_logo_updated_at": "",
    "privacy_notice": "Usiamo i dati necessari per gestire account, sicurezza e percorso di studio. Nessuna pubblicità o profilazione commerciale.",
    "privacy_controller_name": "Titolare della demo",
    "privacy_controller_address": "",
    "privacy_contact_email": "privacy@example.com",
    "privacy_pec_email": "privacy@pec.example.com",
    "privacy_dpo_contact": "",
    "privacy_hosting_location": "Italia (server autogestito)",
    "privacy_email_provider": "Fornitore SMTP configurato dall'amministratore",
    "privacy_transfer_note": "Le sole email di servizio possono essere trattate dal fornitore SMTP anche fuori dallo Spazio economico europeo, secondo le garanzie applicabili dichiarate dal fornitore.",
    "privacy_policy_version": "2026-08-14",
    "privacy_effective_date": "2026-08-14",
    "privacy_audit_log_days": 180,
    "privacy_backup_days": 30,
    "exam_config": {
        "examPlan": {"storia": 8, "logica": 12, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4},
        "logicPlan": {"deduzioni": 2, "serie": 2, "verbale": 2, "calcolo": 1, "figure": 1, "insiemi": 1, "relazioni": 1, "ordinamenti": 1, "brani": 0, "mista": 1},
    },
    "daily_challenge_config": {
        "examPlan": {"storia": 8, "logica": 12, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4},
        "logicPlan": {"deduzioni": 2, "serie": 2, "verbale": 2, "calcolo": 1, "figure": 1, "insiemi": 1, "relazioni": 1, "ordinamenti": 1, "brani": 0, "mista": 1},
    },
}
SECRET_SETTING_KEYS = {"duckdns_token", "smtp_password"}


async def get_db() -> AsyncGenerator[Session, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_setting(db: Session, key: str) -> Any:
    row = db.get(Setting, key)
    value = row.value if row else DEFAULT_SETTINGS.get(key)
    if key in SECRET_SETTING_KEYS and value:
        try:
            return fernet.decrypt(str(value).encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError):
            return ""
    return value


def set_setting(db: Session, key: str, value: Any) -> None:
    stored = fernet.encrypt(str(value).encode("utf-8")).decode("ascii") if key in SECRET_SETTING_KEYS and value else value
    row = db.get(Setting, key)
    if row:
        row.value = stored
    else:
        db.add(Setting(key=key, value=stored))


def port_control_status() -> dict[str, Any]:
    if not PORT_CONTROL_DIR:
        return {"available": False, "state": "disabled"}
    status_file = PORT_CONTROL_DIR / "status.json"
    try:
        data = json.loads(status_file.read_text(encoding="utf-8"))
        return {"available": True, **(data if isinstance(data, dict) else {})}
    except (OSError, ValueError, json.JSONDecodeError):
        return {"available": True, "state": "ready"}


def semantic_version(value: str) -> tuple[int, int, int] | None:
    match = VERSION_RE.fullmatch(str(value).strip())
    return tuple(int(part) for part in match.groups()) if match else None


def read_control_json(name: str) -> dict[str, Any] | None:
    if not PORT_CONTROL_DIR:
        return None
    try:
        value = json.loads((PORT_CONTROL_DIR / name).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def write_control_json(name: str, payload: dict[str, Any]) -> None:
    if not PORT_CONTROL_DIR:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Il controllo del portale non è installato su questo server.")
    try:
        PORT_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
        temporary = PORT_CONTROL_DIR / f".{name}-{uuid.uuid4().hex}.tmp"
        temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        temporary.replace(PORT_CONTROL_DIR / name)
    except OSError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Impossibile comunicare con il controllo del server.") from error


def portal_control_status() -> dict[str, Any]:
    if not PORT_CONTROL_DIR:
        return {"available": False, "state": "disabled"}
    data = read_control_json("server-status.json")
    return {"available": True, **(data or {"state": "ready"})}


def public_update_metadata(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if not data:
        return None
    hidden = {"assetUrl", "filePath", "requestedBy"}
    return {key: value for key, value in data.items() if key not in hidden}


def create_portal_request(action: str, admin: "User", **details: Any) -> dict[str, Any]:
    if not PORT_CONTROL_DIR:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Installa prima il controllo aggiornamenti sul server.")
    if (PORT_CONTROL_DIR / "server-request.json").exists() or (PORT_CONTROL_DIR / "server-request.processing.json").exists():
        raise HTTPException(status.HTTP_409_CONFLICT, "È già in corso un'operazione sul portale.")
    current_status = portal_control_status()
    if current_status.get("state") in {"backing-up", "downloading", "installing", "restarting", "stopping"}:
        raise HTTPException(status.HTTP_409_CONFLICT, "È già in corso un'operazione sul portale.")
    request_id = str(uuid.uuid4())
    payload = {
        "requestId": request_id,
        "action": action,
        "requestedAt": utcnow().isoformat(),
        "requestedBy": admin.id,
        "currentVersion": APP_VERSION,
        **details,
    }
    write_control_json("server-request.json", payload)
    return payload


def inspect_update_archive(path: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if not names or len(names) > 5000:
                raise ValueError("Pacchetto vuoto o troppo complesso.")
            for name in names:
                normalized = name.replace("\\", "/")
                parts = [part for part in normalized.split("/") if part]
                if normalized.startswith("/") or ".." in parts or (parts and ":" in parts[0]):
                    raise ValueError("Il pacchetto contiene percorsi non sicuri.")
            if "release-manifest.json" not in names or "version.json" not in names:
                raise ValueError("Non è un pacchetto server Quiz 400 VVF valido.")
            manifest = json.loads(archive.read("release-manifest.json"))
            version_file = json.loads(archive.read("version.json"))
    except (OSError, zipfile.BadZipFile, KeyError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error) or "Pacchetto di aggiornamento non valido.") from error
    if not isinstance(manifest, dict) or manifest.get("app") != "Quiz 400 VVF 2026 Server":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Manifest del pacchetto non valido.")
    version = str(manifest.get("version") or version_file.get("version") or "").removeprefix("v")
    if not semantic_version(version) or str(version_file.get("version")) != version:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Versione del pacchetto non valida o incoerente.")
    files = manifest.get("files")
    if not isinstance(files, list) or not files or any(not isinstance(item, dict) or not item.get("path") or not item.get("sha256") for item in files):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Elenco file del pacchetto non valido.")
    changelog = manifest.get("changelog", "")
    if isinstance(changelog, list):
        changelog = "\n".join(f"• {item}" for item in changelog if isinstance(item, str))
    return {
        "version": version,
        "changelog": str(changelog)[:20000],
        "platform": str(manifest.get("platform") or "Linux e Windows"),
    }


def public_settings(db: Session) -> dict[str, Any]:
    logo_version = str(get_setting(db, "brand_logo_updated_at") or "default")
    logo_customized = bool(get_setting(db, "brand_logo_data"))
    privacy = {
        "controllerName": get_setting(db, "privacy_controller_name"),
        "controllerAddress": get_setting(db, "privacy_controller_address"),
        "contactEmail": get_setting(db, "privacy_contact_email"),
        "pecEmail": get_setting(db, "privacy_pec_email"),
        "dpoContact": get_setting(db, "privacy_dpo_contact"),
        "hostingLocation": get_setting(db, "privacy_hosting_location"),
        "emailProvider": get_setting(db, "privacy_email_provider"),
        "transferNote": get_setting(db, "privacy_transfer_note"),
        "policyVersion": get_setting(db, "privacy_policy_version"),
        "effectiveDate": get_setting(db, "privacy_effective_date"),
        "sessionDays": int(get_setting(db, "session_days") or 30),
        "resetTokenMinutes": int(get_setting(db, "reset_token_minutes") or 30),
        "auditLogDays": int(get_setting(db, "privacy_audit_log_days") or 180),
        "backupDays": int(get_setting(db, "privacy_backup_days") or 30),
    }
    privacy["complete"] = bool(privacy["controllerName"] and privacy["contactEmail"])
    return {
        "siteName": get_setting(db, "site_name"),
        "registrationEnabled": bool(get_setting(db, "registration_enabled")),
        "dailyChallengeEnabled": bool(get_setting(db, "daily_challenge_enabled")),
        "dailyChallengeRequired": bool(get_setting(db, "daily_challenge_required")),
        "emailResetEnabled": bool(get_setting(db, "smtp_enabled") and get_setting(db, "smtp_host")),
        "privacyNotice": get_setting(db, "privacy_notice"),
        "privacy": privacy,
        "examConfig": get_setting(db, "exam_config"),
        "logoUrl": f"./api/branding/logo?v={logo_version}",
        "logoCustomized": logo_customized,
        "logoMime": str(get_setting(db, "brand_logo_mime") or "image/jpeg") if logo_customized else "image/jpeg",
    }


def normalize_username(value: str) -> str:
    username = value.strip().lower()
    if not USERNAME_RE.fullmatch(username):
        raise ValueError("Usa 3-40 caratteri: lettere minuscole, numeri, punto, trattino o underscore.")
    return username


def normalize_email(value: str | None) -> str | None:
    return value.strip().lower() if value and value.strip() else None


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    return (forwarded or (request.client.host if request.client else ""))[:64]


def audit(db: Session, action: str, request: Request, actor: str | None = None, target: str | None = None, **details: Any) -> None:
    db.add(AuditLog(actor_user_id=actor, target_user_id=target, action=action, details=details, ip_address=client_ip(request)))


def empty_state() -> dict[str, Any]:
    return {"progress": {}, "sessions": [], "categoryCursor": {}, "examCursor": {}, "examCount": 0, "quizGenerationCount": 0, "quizRotation": {}, "fortyQuestionExposure": {}, "examPresets": [], "activeExamPresetId": None, "theme": "system", "deepLearning": {"enabled": False, "tracks": {}}, "deepLearningIntroSeen": False, "releaseNotesSeen": "", "studyPaths": {"resources": {}, "lastResourceId": None, "checkpoints": {}}, "dailyChallengeReminders": {}}


def serialize_user(user: User, include_state: bool = False) -> dict[str, Any]:
    payload = {
        "id": user.id,
        "username": user.username,
        "name": user.display_name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
        "approved": user.approved,
        "mustChangePassword": user.must_change_password,
        "createdAt": user.created_at.isoformat(),
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "privacyPolicyVersion": user.privacy_policy_version,
        "privacyAcknowledgedAt": user.privacy_acknowledged_at.isoformat() if user.privacy_acknowledged_at else None,
        "avatarUrl": f"./api/users/{user.id}/avatar",
    }
    if include_state:
        payload["state"] = user.state.data if user.state else empty_state()
        payload["revision"] = user.state.revision if user.state else 0
    return payload


def daily_challenge_gate_payload(user: User, db: Session) -> dict[str, Any]:
    today = challenge_today()
    enabled = bool(get_setting(db, "daily_challenge_enabled"))
    required = enabled and bool(get_setting(db, "daily_challenge_required")) and user.role != "admin"
    attempt = user_challenge_attempt(db, today, user.id)
    if attempt and not attempt.submitted_at:
        challenge = db.get(DailyChallenge, today)
        if challenge and utcnow() >= challenge_expiry(attempt):
            finalize_challenge_attempt(attempt, challenge, challenge_expiry(attempt))
            record_challenge_in_user_state(user, attempt, challenge)
            db.commit()
    status_value = "completed" if attempt and attempt.submitted_at else "active" if attempt else "not_started"
    return {
        "required": required,
        "completed": not required or status_value == "completed",
        "date": today.isoformat(),
        "status": status_value,
    }


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def secure_request(request: Request) -> bool:
    return request.headers.get("x-forwarded-proto", request.url.scheme).split(",", 1)[0].strip() == "https"


def create_session(db: Session, user: User, request: Request, response: Response) -> None:
    raw = secrets.token_urlsafe(48)
    days = max(1, min(365, int(get_setting(db, "session_days") or 30)))
    expires = utcnow() + timedelta(days=days)
    db.add(LoginSession(user_id=user.id, token_hash=token_hash(raw), expires_at=expires, ip_address=client_ip(request), user_agent=request.headers.get("user-agent", "")[:300]))
    response.set_cookie(SESSION_COOKIE, raw, max_age=days * 86400, expires=expires, httponly=True, secure=secure_request(request), samesite="lax", path="/")


def current_user_optional(request: Request, db: Session) -> User | None:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    login_session = db.scalar(select(LoginSession).where(LoginSession.token_hash == token_hash(raw), LoginSession.expires_at > utcnow()))
    if not login_session:
        return None
    user = db.get(User, login_session.user_id)
    return user if user and user.active and user.approved else None


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = current_user_optional(request, db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Accesso richiesto.")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Permessi amministratore richiesti.")
    return user


def require_dashboard_reader(user: User = Depends(require_user)) -> User:
    if user.role not in {"admin", "moderator"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Permessi Dashboard richiesti.")
    return user


rate_buckets: dict[str, deque[float]] = defaultdict(deque)
rate_lock = threading.Lock()


def enforce_rate_limit(request: Request, scope: str, limit: int, window_seconds: int) -> None:
    key = f"{scope}:{client_ip(request)}"
    now = time.monotonic()
    with rate_lock:
        bucket = rate_buckets[key]
        while bucket and bucket[0] < now - window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Troppi tentativi. Riprova più tardi.")
        bucket.append(now)


class LoginInput(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=256)


class RegistrationInput(LoginInput):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class PublicRegistrationInput(RegistrationInput):
    privacy_acknowledged: bool
    privacy_policy_version: str = Field(min_length=1, max_length=40)


class ForgotInput(BaseModel):
    account: str = Field(min_length=3, max_length=254)


class ResetInput(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    password: str = Field(min_length=10, max_length=256)


class ChangePasswordInput(BaseModel):
    current_password: str = Field(min_length=8, max_length=256)
    new_password: str = Field(min_length=10, max_length=256)


class ProfileInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr | None = None


class ProfileAvatarInput(BaseModel):
    data_url: str = Field(min_length=32, max_length=1_500_000)


class StateInput(BaseModel):
    state: dict[str, Any]
    config: dict[str, Any] | None = None


class DailyChallengeAnswersInput(BaseModel):
    answers: list[int | None] = Field(min_length=40, max_length=40)
    questionSeconds: list[int] | None = Field(default=None, min_length=40, max_length=40)


class AdminUserInput(RegistrationInput):
    role: str = "user"

    @field_validator("role")
    @classmethod
    def role_is_valid(cls, value: str) -> str:
        if value not in {"user", "moderator", "admin"}:
            raise ValueError("Ruolo non valido.")
        return value


class AdminUserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    active: bool | None = None
    approved: bool | None = None
    role: str | None = None


class AdminResetInput(BaseModel):
    password: str | None = Field(default=None, min_length=10, max_length=256)


class PortChangeInput(BaseModel):
    app_port: int = Field(ge=1024, le=65535)


class UpdateInstallInput(BaseModel):
    source: Literal["github", "upload"]


class BrandLogoInput(BaseModel):
    data_url: str = Field(min_length=32, max_length=1_500_000)


class DashboardSettingsInput(BaseModel):
    theoretical_cutoff: float = Field(ge=-13.2, le=40)


class CloudSettingsInput(BaseModel):
    site_name: str = Field(min_length=3, max_length=100)
    registration_enabled: bool
    daily_challenge_enabled: bool = True
    daily_challenge_required: bool = False
    daily_challenge_config: dict[str, Any] | None = None
    public_url: str = Field(default="", max_length=300)
    session_days: int = Field(ge=1, le=365)
    reset_token_minutes: int = Field(ge=10, le=1440)
    privacy_notice: str = Field(default="", max_length=2000)
    privacy_controller_name: str = Field(default="", max_length=200)
    privacy_controller_address: str = Field(default="", max_length=300)
    privacy_contact_email: EmailStr | None = None
    privacy_pec_email: EmailStr | None = None
    privacy_dpo_contact: str = Field(default="", max_length=300)
    privacy_hosting_location: str = Field(default="", max_length=300)
    privacy_email_provider: str = Field(default="", max_length=300)
    privacy_transfer_note: str = Field(default="", max_length=1500)
    privacy_policy_version: str = Field(min_length=1, max_length=40)
    privacy_effective_date: str = Field(min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    privacy_audit_log_days: int = Field(ge=30, le=730)
    privacy_backup_days: int = Field(ge=1, le=365)
    duckdns_enabled: bool
    duckdns_domain: str = Field(default="", max_length=80)
    duckdns_token: str = Field(default="", max_length=200)
    duckdns_interval_minutes: int = Field(ge=5, le=1440)
    clear_duckdns_token: bool = False
    smtp_enabled: bool
    smtp_host: str = Field(default="", max_length=254)
    smtp_port: int = Field(ge=1, le=65535)
    smtp_username: str = Field(default="", max_length=254)
    smtp_password: str = Field(default="", max_length=300)
    smtp_from_email: EmailStr | None = None
    smtp_use_tls: bool = True
    clear_smtp_password: bool = False

    @field_validator("public_url")
    @classmethod
    def public_url_is_valid(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if value and (urlparse(value).scheme not in {"http", "https"} or not urlparse(value).hostname):
            raise ValueError("URL pubblico non valido.")
        return value
    @field_validator("duckdns_domain")
    @classmethod
    def duckdns_domain_is_valid(cls, value: str) -> str:
        value = value.strip().lower()
        if value and not DUCKDNS_RE.fullmatch(value):
            raise ValueError("Dominio DuckDNS non valido.")
        return value.removesuffix(".duckdns.org")


class DailyChallengeSettingsInput(BaseModel):
    enabled: bool = True
    required: bool = False
    config: dict[str, Any]


QUESTION_REPORT_REASONS = {
    "question": "Testo o domanda errata",
    "answer": "Risposta corretta errata",
    "explanation": "Spiegazione errata o illeggibile",
    "image": "Immagine mancante o errata",
    "other": "Altro",
}


class QuestionReportInput(BaseModel):
    question_id: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=40)
    note: str = Field(default="", max_length=1500)

    @field_validator("reason")
    @classmethod
    def reason_is_valid(cls, value: str) -> str:
        if value not in QUESTION_REPORT_REASONS:
            raise ValueError("Motivo della segnalazione non valido.")
        return value


class QuestionModerationInput(BaseModel):
    reason: str = Field(default="", max_length=1500)
    reply: str = Field(default="", max_length=4000)


class QuestionReportReplyInput(BaseModel):
    reply: str = Field(default="", max_length=4000)


class QuestionRatingInput(BaseModel):
    rating: int = Field(ge=1, le=3)


def numeric_value(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def session_accuracy(session: dict[str, Any]) -> float | None:
    stored = numeric_value(session.get("accuracy"))
    if stored is not None:
        return stored
    correct = numeric_value(session.get("correct")) or 0
    wrong = numeric_value(session.get("wrong")) or 0
    answered = correct + wrong
    return round(correct / answered * 100, 1) if answered else None


def session_score(session: dict[str, Any]) -> float | None:
    stored = numeric_value(session.get("score"))
    if stored is not None:
        return stored
    correct = numeric_value(session.get("correct"))
    wrong = numeric_value(session.get("wrong"))
    if correct is None and wrong is None:
        return None
    return round((correct or 0) - (wrong or 0) * 0.33, 2)


def average(values: list[float], digits: int = 2) -> float | None:
    return round(sum(values) / len(values), digits) if values else None


def session_group_statistics(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [value for session in sessions if (value := session_score(session)) is not None]
    accuracies = [value for session in sessions if (value := session_accuracy(session)) is not None]
    question_counts = [
        value for session in sessions if (value := numeric_value(session.get("questionCount"))) is not None
    ]
    return {
        "count": len(sessions),
        "averageScore": average(scores),
        "bestScore": max(scores) if scores else None,
        "averageAccuracy": average(accuracies, 1),
        "averageQuestions": average(question_counts, 1),
    }


def macro_question_category(value: Any) -> str:
    category = str(value or "")
    return "logica" if category in {"logica", "brani", "insiemi"} else category


def subject_session_statistics(state_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sessions = state_data.get("sessions", []) if isinstance(state_data, dict) else []
    sessions = sessions if isinstance(sessions, list) else []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        if not isinstance(session, dict) or session.get("type") not in {"study", "guided", "tutor"}:
            continue
        per_category = session.get("perCategory")
        if isinstance(per_category, dict) and per_category:
            for category, payload in per_category.items():
                if not isinstance(payload, dict):
                    continue
                correct = numeric_value(payload.get("correct")) or 0
                wrong = numeric_value(payload.get("wrong")) or 0
                blank = numeric_value(payload.get("blank")) or 0
                grouped.setdefault(macro_question_category(category), []).append(
                    {
                        **payload,
                        "score": round(correct - wrong * 0.33, 2),
                        "questionCount": numeric_value(payload.get("total")) or correct + wrong + blank,
                    }
                )
            continue
        category = session.get("category")
        if isinstance(category, str) and category:
            grouped.setdefault(macro_question_category(category), []).append(session)
    return {category: session_group_statistics(rows) for category, rows in grouped.items()}


def state_statistics(state_data: dict[str, Any]) -> dict[str, Any]:
    progress = state_data.get("progress") if isinstance(state_data, dict) else {}
    sessions = state_data.get("sessions") if isinstance(state_data, dict) else []
    progress = progress if isinstance(progress, dict) else {}
    sessions = sessions if isinstance(sessions, list) else []
    values = [item for item in progress.values() if isinstance(item, dict)]
    study_paths = state_data.get("studyPaths", {}) if isinstance(state_data, dict) else {}
    study_resources = study_paths.get("resources", {}) if isinstance(study_paths, dict) else {}
    study_values = [item for item in study_resources.values() if isinstance(item, dict)] if isinstance(study_resources, dict) else []
    valid_sessions = [item for item in sessions if isinstance(item, dict)]
    exams = [item for item in valid_sessions if item.get("type") in {"exam", "daily-challenge"}]
    forty_quizzes = [item for item in valid_sessions if item.get("type") in {"exam", "guided-exam", "daily-challenge"}]
    guided = [item for item in sessions if isinstance(item, dict) and item.get("type") in {"guided", "guided-exam"}]
    subject_quizzes = [item for item in sessions if isinstance(item, dict) and item.get("type") in {"study", "guided", "tutor"}]
    exam_stats = session_group_statistics(exams)
    forty_stats = session_group_statistics(forty_quizzes)
    subject_stats = session_group_statistics(subject_quizzes)
    accuracies = [value for item in valid_sessions if (value := session_accuracy(item)) is not None]
    return {
        "answered": sum(1 for item in values if int(item.get("attempts", 0) or 0) > 0),
        "known": sum(1 for item in values if item.get("status") == "known"),
        "review": sum(1 for item in values if item.get("status") == "review"),
        "unknown": sum(1 for item in values if item.get("status") == "unknown"),
        "unanswered": sum(1 for item in values if item.get("status") == "unanswered"),
        "simulations": len(exams),
        "guidedQuizzes": len(guided),
        "subjectQuizzes": len(subject_quizzes),
        "fortyQuizzes": forty_stats["count"],
        "guidedFortyQuizzes": sum(1 for item in forty_quizzes if item.get("type") == "guided-exam"),
        "dailyChallenges": sum(1 for item in forty_quizzes if item.get("type") == "daily-challenge"),
        "sessions": len(sessions),
        "averageScore": exam_stats["averageScore"],
        "bestScore": exam_stats["bestScore"],
        "averageFortyScore": forty_stats["averageScore"],
        "bestFortyScore": forty_stats["bestScore"],
        "averageFortyAccuracy": forty_stats["averageAccuracy"],
        "averageSubjectScore": subject_stats["averageScore"],
        "bestSubjectScore": subject_stats["bestScore"],
        "averageSubjectAccuracy": subject_stats["averageAccuracy"],
        "averageAccuracy": average(accuracies, 1),
        "studyResourcesStarted": sum(1 for item in study_values if item.get("status") == "started"),
        "studyResourcesCompleted": sum(1 for item in study_values if item.get("status") == "completed"),
    }


question_bank: list[dict[str, Any]] = []
questions_by_id: dict[str, dict[str, Any]] = {}
question_categories: dict[str, str] = {}
question_category_totals: dict[str, int] = {}


def load_question_categories() -> None:
    global question_bank, questions_by_id, question_categories, question_category_totals
    try:
        rows = json.loads((ROOT / "quiz-dataset.json").read_text(encoding="utf-8"))
        question_bank = [row for row in rows if isinstance(row, dict) and row.get("id") and row.get("category") and isinstance(row.get("answers"), list)]
        questions_by_id = {str(row["id"]): row for row in question_bank}
        question_categories = {str(row["id"]): macro_question_category(row["category"]) for row in question_bank}
        question_category_totals = {}
        for category in question_categories.values():
            question_category_totals[category] = question_category_totals.get(category, 0) + 1
    except (OSError, ValueError):
        question_bank = []
        questions_by_id = {}
        question_categories = {}
        question_category_totals = {}


def disabled_question_ids(db: Session) -> set[str]:
    return {str(question_id) for question_id in db.scalars(select(DisabledQuestion.question_id)).all()}


def available_question_bank(db: Session) -> list[dict[str, Any]]:
    disabled = disabled_question_ids(db)
    return [question for question in question_bank if str(question["id"]) not in disabled]


def admin_question_payload(question_id: str) -> dict[str, Any]:
    question = questions_by_id.get(str(question_id))
    if not question:
        return {"id": str(question_id), "category": "", "text": "Quesito non più presente nella banca dati.", "answers": [], "correct": None, "explanation": "", "image": ""}
    return {
        "id": str(question["id"]),
        "category": str(question.get("category") or ""),
        "text": str(question.get("text") or ""),
        "answers": [str(answer) for answer in question.get("answers", [])],
        "correct": int(question["correct"]) if isinstance(question.get("correct"), int) else None,
        "explanation": str(question.get("explanation") or ""),
        "image": str(question.get("image") or ""),
    }


def serialize_question_report(report: QuestionReport, db: Session) -> dict[str, Any]:
    reporter = db.get(User, report.user_id) if report.user_id else None
    reviewer = db.get(User, report.reviewed_by_user_id) if report.reviewed_by_user_id else None
    return {
        "id": report.id,
        "questionId": report.question_id,
        "question": admin_question_payload(report.question_id),
        "reporter": reporter.display_name if reporter else "Account non più disponibile",
        "reason": report.reason,
        "reasonLabel": QUESTION_REPORT_REASONS.get(report.reason, report.reason),
        "note": report.note,
        "status": report.status,
        "createdAt": aware_utc(report.created_at).isoformat(),
        "reviewedAt": aware_utc(report.reviewed_at).isoformat() if report.reviewed_at else None,
        "reviewedBy": reviewer.display_name if reviewer else None,
        "reply": report.reply,
        "replyReadAt": aware_utc(report.reply_read_at).isoformat() if report.reply_read_at else None,
    }


def serialize_disabled_question(row: DisabledQuestion, db: Session) -> dict[str, Any]:
    admin = db.get(User, row.disabled_by_user_id) if row.disabled_by_user_id else None
    return {
        "questionId": row.question_id,
        "question": admin_question_payload(row.question_id),
        "reason": row.reason,
        "disabledAt": aware_utc(row.disabled_at).isoformat(),
        "disabledBy": admin.display_name if admin else None,
    }


def challenge_today() -> date:
    return datetime.now(CHALLENGE_TIMEZONE).date()


def aware_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def deterministic_questions(source: list[dict[str, Any]], count: int, seed: str) -> list[dict[str, Any]]:
    if len(source) < count:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "La banca dati non contiene abbastanza quesiti per creare la sfida giornaliera.")
    return sorted(source, key=lambda row: hashlib.sha256(f"{seed}|{row['id']}".encode("utf-8")).digest())[:count]


def daily_challenge_question_usage(challenge_date: date, db: Session) -> dict[str, tuple[int, date]]:
    usage: dict[str, tuple[int, date]] = {}
    previous_challenges = db.scalars(
        select(DailyChallenge)
        .where(DailyChallenge.challenge_date < challenge_date)
        .order_by(DailyChallenge.challenge_date)
    ).all()
    for challenge in previous_challenges:
        for question_id in challenge.question_ids:
            normalized_id = str(question_id)
            count, _ = usage.get(normalized_id, (0, challenge.challenge_date))
            usage[normalized_id] = (count + 1, challenge.challenge_date)
    return usage


def rotating_daily_questions(
    source: list[dict[str, Any]],
    count: int,
    seed: str,
    usage: dict[str, tuple[int, date]],
) -> list[dict[str, Any]]:
    if len(source) < count:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "La banca dati non contiene abbastanza quesiti per creare la sfida giornaliera.")

    never_used = [row for row in source if str(row["id"]) not in usage]
    selected = deterministic_questions(never_used, min(count, len(never_used)), seed) if never_used else []
    remaining = count - len(selected)
    if not remaining:
        return selected

    selected_ids = {str(row["id"]) for row in selected}
    previously_used = [row for row in source if str(row["id"]) not in selected_ids]
    previously_used.sort(
        key=lambda row: (
            usage.get(str(row["id"]), (0, date.min))[0],
            usage.get(str(row["id"]), (0, date.min))[1],
            hashlib.sha256(f"{seed}|riciclo|{row['id']}".encode("utf-8")).digest(),
        )
    )
    return selected + previously_used[:remaining]


def challenge_logic_topic(question: dict[str, Any]) -> str:
    category = str(question.get("category") or "")
    if category == "insiemi":
        return "insiemi"
    if category == "brani":
        return "brani"
    topic = str(question.get("logicTopic") or "")
    return topic if topic in CHALLENGE_LOGIC_TOPICS else "mista"


def normalize_daily_challenge_config(configured: Any, *, strict: bool = False) -> dict[str, dict[str, int]]:
    defaults = DEFAULT_SETTINGS["daily_challenge_config"]
    configured = configured if isinstance(configured, dict) else defaults
    raw_plan = configured.get("examPlan") if isinstance(configured.get("examPlan"), dict) else defaults["examPlan"]
    categories = ("storia", "logica", "fisica", "chimica", "informatica", "inglese")
    try:
        plan = {category: max(0, min(40, int(raw_plan.get(category, 0) or 0))) for category in categories}
    except (TypeError, ValueError):
        plan = dict(defaults["examPlan"])
    if sum(plan.values()) != 40:
        if strict:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La composizione della Sfida del giorno deve contenere esattamente 40 domande.")
        plan = dict(defaults["examPlan"])
    raw_logic = configured.get("logicPlan") if isinstance(configured.get("logicPlan"), dict) else defaults["logicPlan"]
    try:
        logic_plan = {topic: max(0, min(40, int(raw_logic.get(topic, 0) or 0))) for topic in CHALLENGE_SELECTABLE_LOGIC_TOPICS}
    except (TypeError, ValueError):
        logic_plan = {topic: int(defaults["logicPlan"].get(topic, 0)) for topic in CHALLENGE_SELECTABLE_LOGIC_TOPICS}
    logic_plan["brani"] = 0
    if sum(logic_plan[topic] for topic in CHALLENGE_SELECTABLE_LOGIC_TOPICS) != plan["logica"]:
        if strict:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La distribuzione delle sottosezioni di Logica deve coincidere con il numero di domande di Logica. I brani non sono ammessi.")
        if plan["logica"] == sum(defaults["logicPlan"].values()):
            logic_plan = dict(defaults["logicPlan"])
        else:
            logic_plan = {topic: 0 for topic in CHALLENGE_LOGIC_TOPICS}
            for index in range(plan["logica"]):
                logic_plan[CHALLENGE_SELECTABLE_LOGIC_TOPICS[index % len(CHALLENGE_SELECTABLE_LOGIC_TOPICS)]] += 1
    logic_plan["brani"] = 0
    return {"examPlan": plan, "logicPlan": logic_plan}


def validate_daily_challenge_capacity(config: dict[str, dict[str, int]], db: Session) -> None:
    plan = config["examPlan"]
    source_bank = available_question_bank(db)
    for category, count in plan.items():
        if not count or category == "logica":
            continue
        available = sum(1 for row in source_bank if macro_question_category(row.get("category")) == category)
        if count > available:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"La banca dati contiene soltanto {available} domande per {category}.")
    logic_source = [row for row in source_bank if macro_question_category(row.get("category")) == "logica"]
    for topic in CHALLENGE_SELECTABLE_LOGIC_TOPICS:
        count = config["logicPlan"].get(topic, 0)
        available = sum(1 for row in logic_source if challenge_logic_topic(row) == topic)
        if count > available:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"La banca dati contiene soltanto {available} domande nella sottosezione Logica “{topic}”.")


def normalized_challenge_composition(db: Session) -> dict[str, dict[str, int]]:
    return normalize_daily_challenge_config(get_setting(db, "daily_challenge_config"))


def build_daily_challenge(challenge_date: date, db: Session) -> DailyChallenge:
    if not question_bank:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Banca dati dei quiz non disponibile.")
    composition = normalized_challenge_composition(db)
    plan = composition["examPlan"]
    logic_plan = composition["logicPlan"]
    active_bank = available_question_bank(db)
    usage = daily_challenge_question_usage(challenge_date, db)
    seed = f"quiz400-daily|{challenge_date.isoformat()}|{APP_VERSION}"
    selected: list[dict[str, Any]] = []
    for category, count in plan.items():
        if not count:
            continue
        if category != "logica":
            source = [row for row in active_bank if macro_question_category(row.get("category")) == category]
            selected.extend(rotating_daily_questions(source, count, f"{seed}|{category}", usage))
            continue
        logic_source = [row for row in active_bank if macro_question_category(row.get("category")) == "logica"]
        for topic, topic_count in logic_plan.items():
            if topic_count:
                source = [row for row in logic_source if challenge_logic_topic(row) == topic]
                selected.extend(rotating_daily_questions(source, topic_count, f"{seed}|logica|{topic}", usage))
    if len(selected) != 40 or len({str(row["id"]) for row in selected}) != 40:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "La composizione della sfida non ha prodotto 40 quesiti distinti.")
    ordered = sorted(selected, key=lambda row: hashlib.sha256(f"{seed}|ordine|{row['id']}".encode("utf-8")).digest())
    return DailyChallenge(challenge_date=challenge_date, question_ids=[str(row["id"]) for row in ordered], composition=composition, app_version=APP_VERSION)


def get_or_create_daily_challenge(challenge_date: date, db: Session) -> DailyChallenge:
    challenge = db.get(DailyChallenge, challenge_date)
    if challenge:
        return challenge
    challenge = build_daily_challenge(challenge_date, db)
    db.add(challenge)
    try:
        db.flush()
        return challenge
    except IntegrityError:
        db.rollback()
        existing = db.get(DailyChallenge, challenge_date)
        if not existing:
            raise
        return existing


def challenge_questions(challenge: DailyChallenge) -> list[dict[str, Any]]:
    questions = [questions_by_id.get(str(question_id)) for question_id in challenge.question_ids]
    if any(question is None for question in questions):
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Una domanda della sfida non è più disponibile nella banca dati.")
    return [question for question in questions if question is not None]


def public_challenge_question(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(question["id"]),
        "category": str(question.get("category") or ""),
        "text": str(question.get("text") or ""),
        "answers": [str(answer) for answer in question.get("answers", [])],
        "image": str(question.get("image") or ""),
    }


def validate_challenge_answers(challenge: DailyChallenge, answers: list[int | None]) -> list[int | None]:
    questions = challenge_questions(challenge)
    if len(answers) != len(questions):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Sono richieste esattamente 40 risposte.")
    normalized: list[int | None] = []
    for answer, question in zip(answers, questions, strict=True):
        if answer is None:
            normalized.append(None)
        elif isinstance(answer, bool) or answer < 0 or answer >= len(question.get("answers", [])):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Una delle risposte selezionate non è valida.")
        else:
            normalized.append(int(answer))
    return normalized


def challenge_expiry(attempt: DailyChallengeAttempt) -> datetime:
    return aware_utc(attempt.started_at) + timedelta(seconds=CHALLENGE_SECONDS)


def validate_challenge_question_seconds(values: list[int] | None, question_count: int) -> list[int] | None:
    if values is None:
        return None
    if len(values) != question_count:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "I tempi delle domande non sono completi.")
    normalized: list[int] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > CHALLENGE_SECONDS:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Uno dei tempi delle domande non è valido.")
        normalized.append(value)
    return normalized


def finalize_challenge_attempt(attempt: DailyChallengeAttempt, challenge: DailyChallenge, submitted_at: datetime | None = None) -> DailyChallengeAttempt:
    if attempt.submitted_at:
        return attempt
    questions = challenge_questions(challenge)
    answers = validate_challenge_answers(challenge, list(attempt.answers or [None] * len(questions)))
    correct = sum(1 for answer, question in zip(answers, questions, strict=True) if answer is not None and answer == int(question["correct"]))
    wrong = sum(1 for answer, question in zip(answers, questions, strict=True) if answer is not None and answer != int(question["correct"]))
    blank = len(questions) - correct - wrong
    finished_at = min(submitted_at or utcnow(), challenge_expiry(attempt))
    attempt.answers = answers
    attempt.submitted_at = finished_at
    attempt.correct = correct
    attempt.wrong = wrong
    attempt.blank = blank
    attempt.score_x100 = correct * 100 - wrong * 33
    attempt.duration_seconds = max(0, min(CHALLENGE_SECONDS, int((aware_utc(finished_at) - aware_utc(attempt.started_at)).total_seconds())))
    return attempt


def challenge_result_details(attempt: DailyChallengeAttempt, challenge: DailyChallenge) -> list[dict[str, Any]]:
    details = []
    questions = challenge_questions(challenge)
    question_seconds = attempt.question_seconds if isinstance(attempt.question_seconds, list) and len(attempt.question_seconds) == len(questions) else [None] * len(questions)
    for answer, question, response_seconds in zip(attempt.answers, questions, question_seconds, strict=True):
        correct_index = int(question["correct"])
        details.append({
            **public_challenge_question(question),
            "questionNumber": len(details) + 1,
            "correct": correct_index,
            "explanation": str(question.get("explanation") or ""),
            "choice": answer,
            "blank": answer is None,
            "isCorrect": answer is not None and answer == correct_index,
            "responseSeconds": response_seconds,
        })
    return details


def challenge_score(attempt: DailyChallengeAttempt) -> float | None:
    return round(attempt.score_x100 / 100, 2) if attempt.score_x100 is not None else None


def record_challenge_in_user_state(user: User, attempt: DailyChallengeAttempt, challenge: DailyChallenge) -> None:
    if not attempt.submitted_at:
        return
    state_data = dict(user.state.data if user.state and isinstance(user.state.data, dict) else empty_state())
    recorded = list(state_data.get("dailyChallengeRecordedDates") or [])
    key = challenge.challenge_date.isoformat()
    if key in recorded:
        return
    progress = dict(state_data.get("progress") or {})
    review: list[dict[str, Any]] = []
    per_category: dict[str, dict[str, int]] = {}
    completed_at = aware_utc(attempt.submitted_at).isoformat()
    for answer, question in zip(attempt.answers, challenge_questions(challenge), strict=True):
        question_id = str(question["id"])
        correct_index = int(question["correct"])
        is_blank = answer is None
        is_correct = answer is not None and answer == correct_index
        item = dict(progress.get(question_id) or {"attempts": 0, "correct": 0, "wrong": 0, "skipped": 0, "status": "unanswered"})
        if is_blank:
            item["skipped"] = int(item.get("skipped", 0) or 0) + 1
            if not int(item.get("attempts", 0) or 0):
                item["status"] = "unanswered"
        else:
            item["attempts"] = int(item.get("attempts", 0) or 0) + 1
            if is_correct:
                item["correct"] = int(item.get("correct", 0) or 0) + 1
                item["status"] = "known"
            else:
                item["wrong"] = int(item.get("wrong", 0) or 0) + 1
                item["status"] = "review"
        item["lastAt"] = completed_at
        progress[question_id] = item
        category = macro_question_category(question.get("category"))
        bucket = per_category.setdefault(category, {"correct": 0, "wrong": 0, "blank": 0, "total": 0})
        bucket["total"] += 1
        bucket["blank" if is_blank else "correct" if is_correct else "wrong"] += 1
        review.append({
            "id": question_id,
            "category": category,
            "logicTopic": challenge_logic_topic(question) if category == "logica" else None,
            "choiceText": None if is_blank else str(question["answers"][answer]),
            "correctText": str(question["answers"][correct_index]),
            "blank": is_blank,
            "correct": is_correct,
        })
    for bucket in per_category.values():
        answered = bucket["correct"] + bucket["wrong"]
        bucket["accuracy"] = round(bucket["correct"] / answered * 100) if answered else None
    sessions = list(state_data.get("sessions") or [])
    sessions.append({
        "id": f"daily-challenge-{key}",
        "type": "daily-challenge",
        "at": completed_at,
        "challengeDate": key,
        "correct": attempt.correct,
        "wrong": attempt.wrong,
        "blank": attempt.blank,
        "score": challenge_score(attempt),
        "accuracy": round((attempt.correct or 0) / max(1, (attempt.correct or 0) + (attempt.wrong or 0)) * 100),
        "questionCount": 40,
        "perCategory": per_category,
        "review": review,
        "durationSeconds": attempt.duration_seconds,
    })
    sessions_with_review = [item for item in sessions if isinstance(item, dict) and isinstance(item.get("review"), list)]
    for item in sessions_with_review[:-5]:
        item.pop("review", None)
    recorded.append(key)
    state_data["progress"] = progress
    state_data["sessions"] = sessions
    state_data["dailyChallengeRecordedDates"] = recorded[-400:]
    if not user.state:
        user.state = UserState(data=state_data, revision=1)
    else:
        user.state.data = state_data
        user.state.revision += 1
        user.state.updated_at = utcnow()


def challenge_leaderboard(db: Session, challenge_date: date, current_user_id: str, include_attempt_ids: bool = False) -> dict[str, Any]:
    rows = db.execute(
        select(DailyChallengeAttempt, User)
        .join(User, User.id == DailyChallengeAttempt.user_id)
        .where(DailyChallengeAttempt.challenge_date == challenge_date, DailyChallengeAttempt.submitted_at.is_not(None))
    ).all()
    ordered = sorted(rows, key=lambda row: (-(row[0].score_x100 or 0), -(row[0].correct or 0), row[0].wrong or 0, row[0].duration_seconds or CHALLENGE_SECONDS, aware_utc(row[0].submitted_at)))
    entries = [
        {
            "rank": index + 1,
            "displayName": user.display_name,
            "avatarUrl": f"./api/users/{user.id}/avatar",
            "score": challenge_score(attempt),
            "correct": attempt.correct,
            "wrong": attempt.wrong,
            "blank": attempt.blank,
            "durationSeconds": attempt.duration_seconds,
            "submittedAt": aware_utc(attempt.submitted_at).isoformat(),
            "isCurrentUser": attempt.user_id == current_user_id,
            **({"attemptId": attempt.id} if include_attempt_ids else {}),
        }
        for index, (attempt, user) in enumerate(ordered)
    ]
    current = next((entry for entry in entries if entry["isCurrentUser"]), None)
    return {"date": challenge_date.isoformat(), "participants": len(entries), "entries": entries[:50], "currentUser": current, "theoreticalCutoff": round(float(get_setting(db, "theoretical_cutoff")), 2)}


def serialize_daily_challenge(challenge: DailyChallenge, attempt: DailyChallengeAttempt | None, db: Session, user: User) -> dict[str, Any]:
    now = utcnow()
    if attempt and not attempt.submitted_at and now >= challenge_expiry(attempt):
        finalize_challenge_attempt(attempt, challenge, challenge_expiry(attempt))
        record_challenge_in_user_state(user, attempt, challenge)
        db.commit()
    elif attempt and attempt.submitted_at:
        record_challenge_in_user_state(user, attempt, challenge)
        db.commit()
    status_value = "completed" if attempt and attempt.submitted_at else "active" if attempt else "not_started"
    payload: dict[str, Any] = {
        "date": challenge.challenge_date.isoformat(),
        "status": status_value,
        "durationSeconds": CHALLENGE_SECONDS,
        "questionCount": len(challenge.question_ids),
        "composition": challenge.composition,
        "leaderboard": challenge_leaderboard(db, challenge.challenge_date, user.id, user.role in {"admin", "moderator"}),
    }
    if not attempt:
        return payload
    payload.update({
        "startedAt": aware_utc(attempt.started_at).isoformat(),
        "expiresAt": challenge_expiry(attempt).isoformat(),
        "remainingSeconds": max(0, int((challenge_expiry(attempt) - now).total_seconds())) if not attempt.submitted_at else 0,
    })
    if not attempt.submitted_at:
        payload["questions"] = [public_challenge_question(question) for question in challenge_questions(challenge)]
        payload["answers"] = list(attempt.answers)
        payload["questionSeconds"] = list(attempt.question_seconds or [0] * len(challenge.question_ids))
        return payload
    payload.update({
        "submittedAt": aware_utc(attempt.submitted_at).isoformat(),
        "result": {
            "correct": attempt.correct,
            "wrong": attempt.wrong,
            "blank": attempt.blank,
            "score": challenge_score(attempt),
            "durationSeconds": attempt.duration_seconds,
            "questions": challenge_result_details(attempt, challenge),
        },
    })
    return payload


def category_statistics(state_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {
        category: {"total": total, "answered": 0, "known": 0, "review": 0, "unknown": 0, "unanswered": total, "toDo": total, "correctAttempts": 0, "wrongAttempts": 0, "accuracy": None}
        for category, total in question_category_totals.items()
    }
    progress = state_data.get("progress", {}) if isinstance(state_data, dict) else {}
    if not isinstance(progress, dict):
        return result
    for question_id, item in progress.items():
        if not isinstance(item, dict):
            continue
        category = question_categories.get(str(question_id), "altro")
        bucket = result.setdefault(category, {"total": 0, "answered": 0, "known": 0, "review": 0, "unknown": 0, "unanswered": 0, "toDo": 0, "correctAttempts": 0, "wrongAttempts": 0, "accuracy": None})
        if int(item.get("attempts", 0) or 0) > 0:
            bucket["answered"] += 1
        item_status = str(item.get("status") or "unanswered")
        if item_status in {"known", "review", "unknown"}:
            bucket[item_status] += 1
            bucket["unanswered"] = max(0, bucket["unanswered"] - 1)
            bucket["toDo"] = bucket["unanswered"]
        bucket["correctAttempts"] += int(item.get("correct", 0) or 0)
        bucket["wrongAttempts"] += int(item.get("wrong", 0) or 0)
    for bucket in result.values():
        graded = bucket["correctAttempts"] + bucket["wrongAttempts"]
        bucket["accuracy"] = round(bucket["correctAttempts"] / graded * 100) if graded else None
    for category, quiz_stats in subject_session_statistics(state_data).items():
        bucket = result.setdefault(category, {"total": 0, "answered": 0, "known": 0, "review": 0, "unknown": 0, "unanswered": 0, "toDo": 0, "correctAttempts": 0, "wrongAttempts": 0, "accuracy": None})
        bucket.update({
            "quizCount": quiz_stats["count"],
            "averageQuizScore": quiz_stats["averageScore"],
            "bestQuizScore": quiz_stats["bestScore"],
            "averageQuizAccuracy": quiz_stats["averageAccuracy"],
            "averageQuizQuestions": quiz_stats["averageQuestions"],
        })
    for bucket in result.values():
        bucket.setdefault("quizCount", 0)
        bucket.setdefault("averageQuizScore", None)
        bucket.setdefault("bestQuizScore", None)
        bucket.setdefault("averageQuizAccuracy", None)
        bucket.setdefault("averageQuizQuestions", None)
    return result


async def send_email(to_email: str, subject: str, body: str, db: Session) -> None:
    host = str(get_setting(db, "smtp_host") or "")
    port = int(get_setting(db, "smtp_port") or 587)
    username = str(get_setting(db, "smtp_username") or "")
    password = str(get_setting(db, "smtp_password") or "")
    from_email = str(get_setting(db, "smtp_from_email") or username)
    use_tls = bool(get_setting(db, "smtp_use_tls"))
    if not host or not from_email:
        raise RuntimeError("SMTP non configurato.")
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    def deliver() -> None:
        with smtplib.SMTP(host, port, timeout=20) as server:
            if use_tls:
                server.starttls(context=ssl.create_default_context())
            if username:
                server.login(username, password)
            server.send_message(message)

    await asyncio.to_thread(deliver)


async def perform_duckdns_update(db: Session) -> dict[str, Any]:
    domain = str(get_setting(db, "duckdns_domain") or "").removesuffix(".duckdns.org")
    token = str(get_setting(db, "duckdns_token") or "")
    if not domain or not token:
        raise RuntimeError("Dominio o token DuckDNS mancanti.")
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get("https://www.duckdns.org/update", params={"domains": domain, "token": token, "ip": "", "verbose": "true"})
        response.raise_for_status()
    success = response.text.strip().startswith("OK")
    result = {"ok": success, "at": utcnow().isoformat(), "response": response.text.strip()[:500]}
    set_setting(db, "duckdns_last_status", result)
    db.commit()
    if not success:
        raise RuntimeError("DuckDNS ha risposto KO.")
    return result


duckdns_wakeup: asyncio.Event | None = None


async def duckdns_worker(wakeup: asyncio.Event) -> None:
    while True:
        wait_seconds = 300
        try:
            with SessionLocal() as db:
                enabled = bool(get_setting(db, "duckdns_enabled"))
                interval = max(5, min(1440, int(get_setting(db, "duckdns_interval_minutes") or 5)))
                wait_seconds = interval * 60
                if enabled:
                    try:
                        await perform_duckdns_update(db)
                    except Exception as error:
                        set_setting(db, "duckdns_last_status", {"ok": False, "at": utcnow().isoformat(), "response": str(error)[:500]})
                        db.commit()
        except Exception:
            wait_seconds = 60
        wakeup.clear()
        try:
            await asyncio.wait_for(wakeup.wait(), timeout=wait_seconds)
        except TimeoutError:
            pass


def initialize_database() -> None:
    Base.metadata.create_all(engine)
    load_question_categories()
    with SessionLocal() as db:
        for key, value in DEFAULT_SETTINGS.items():
            if not db.get(Setting, key):
                set_setting(db, key, value)
        admin_username = os.environ.get("ADMIN_USERNAME", "admin").strip().lower()
        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if not db.scalar(select(func.count(User.id))):
            if not admin_password or len(admin_password) < 10:
                raise RuntimeError("ADMIN_PASSWORD di almeno 10 caratteri è obbligatoria al primo avvio.")
            try:
                admin_username = normalize_username(admin_username)
            except ValueError as error:
                raise RuntimeError(str(error)) from error
            user = User(username=admin_username, display_name=os.environ.get("ADMIN_NAME", "Amministratore")[:100], email=normalize_email(os.environ.get("ADMIN_EMAIL")), password_hash=password_hasher.hash(admin_password), role="admin", active=True, approved=True)
            user.state = UserState(data=empty_state())
            db.add(user)
        db.execute(LoginSession.__table__.delete().where(LoginSession.expires_at <= utcnow()))
        db.execute(PasswordReset.__table__.delete().where(PasswordReset.expires_at <= utcnow()))
        audit_days = max(30, min(730, int(get_setting(db, "privacy_audit_log_days") or 180)))
        db.execute(AuditLog.__table__.delete().where(AuditLog.created_at < utcnow() - timedelta(days=audit_days)))
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    global duckdns_wakeup
    initialize_database()
    duckdns_wakeup = asyncio.Event()
    task = asyncio.create_task(duckdns_worker(duckdns_wakeup))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    duckdns_wakeup = None


app = FastAPI(title="Quiz 400 VVF 2026 Cloud", version=APP_VERSION, lifespan=lifespan, docs_url=None, redoc_url=None)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.url.path.startswith("/api/"):
        length = int(request.headers.get("content-length", "0") or 0)
        maximum = MAX_UPDATE_BYTES if request.url.path == "/api/admin/update/upload" else MAX_STATE_BYTES
        if length > maximum:
            return JSONResponse({"detail": "Richiesta troppo grande."}, status_code=413)
        origin = request.headers.get("origin")
        if origin:
            parsed = urlparse(origin)
            forwarded_host = request.headers.get("x-forwarded-host", request.headers.get("host", "")).split(",", 1)[0].lower()
            if parsed.netloc.lower() != forwarded_host:
                return JSONResponse({"detail": "Origine non consentita."}, status_code=403)
    with SessionLocal() as redirect_db:
        public_url = str(get_setting(redirect_db, "public_url") or "")
    public_host = urlparse(public_url).hostname if public_url else None
    request_host = request.headers.get("x-forwarded-host", request.headers.get("host", "")).split(":", 1)[0].lower()
    if public_url.startswith("https://") and public_host == request_host and not secure_request(request):
        target = public_url.rstrip("/") + request.url.path
        if request.url.query:
            target += "?" + request.url.query
        return Response(status_code=308, headers={"Location": target})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    embedded_study_pdf = request.url.path.startswith("/study-materials/pdfs/")
    response.headers["X-Frame-Options"] = "SAMEORIGIN" if embedded_study_pdf else "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    frame_ancestors = "'self'" if embedded_study_pdf else "'none'"
    response.headers["Content-Security-Policy"] = f"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors {frame_ancestors}"
    if secure_request(request):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/runtime")
def runtime(db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        release_notes = json.loads((ROOT / "release-notes.json").read_text(encoding="utf-8"))
        if not isinstance(release_notes, dict) or release_notes.get("version") != APP_VERSION:
            release_notes = {}
    except (OSError, ValueError, json.JSONDecodeError):
        release_notes = {}
    return {"mode": "cloud", "version": APP_VERSION, "releaseNotes": release_notes, **public_settings(db)}


@app.get("/api/privacy")
def privacy_information(db: Session = Depends(get_db)) -> dict[str, Any]:
    settings = public_settings(db)
    return {
        "siteName": settings["siteName"],
        "summary": settings["privacyNotice"],
        **settings["privacy"],
    }


def image_signature_matches(mime: str, content: bytes) -> bool:
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    }
    return bool(signatures.get(mime, False))


def decode_image_data_url(data_url: str, maximum: int, label: str) -> tuple[str, bytes, str]:
    match = re.fullmatch(r"data:(image/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=\r\n]+)", data_url.strip())
    if not match:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Usa un'immagine JPEG, PNG o WebP valida.")
    try:
        content = base64.b64decode(match.group(2).replace("\r", "").replace("\n", ""), validate=True)
    except (ValueError, TypeError) as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Immagine non valida.") from error
    mime = match.group(1)
    if not content or len(content) > maximum or not image_signature_matches(mime, content):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{label} deve essere JPEG, PNG o WebP e pesare al massimo 1 MB.")
    return mime, content, base64.b64encode(content).decode("ascii")


def decode_logo_data_url(data_url: str) -> tuple[str, bytes, str]:
    return decode_image_data_url(data_url, MAX_LOGO_BYTES, "Il logo")


@app.get("/api/branding/logo")
def branding_logo(db: Session = Depends(get_db)) -> Response:
    encoded = str(get_setting(db, "brand_logo_data") or "")
    mime = str(get_setting(db, "brand_logo_mime") or "image/jpeg")
    if encoded:
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError):
            content = b""
        if content:
            return Response(content=content, media_type=mime, headers={"Cache-Control": "public, max-age=3600"})
    return FileResponse(ROOT / "logo-vvf.jpg", media_type="image/jpeg", headers={"Cache-Control": "public, max-age=3600"})


@app.post("/api/admin/branding/logo")
def save_branding_logo(payload: BrandLogoInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    mime, _, encoded = decode_logo_data_url(payload.data_url)
    updated_at = utcnow().isoformat()
    set_setting(db, "brand_logo_data", encoded)
    set_setting(db, "brand_logo_mime", mime)
    set_setting(db, "brand_logo_updated_at", updated_at)
    audit(db, "admin.brand_logo_updated", request, actor=admin.id, target=admin.id, mime=mime)
    db.commit()
    return {"message": "Logo aggiornato in tutto il portale.", "logoUrl": f"./api/branding/logo?v={updated_at}", "logoCustomized": True}


@app.delete("/api/admin/branding/logo")
def reset_branding_logo(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    updated_at = utcnow().isoformat()
    set_setting(db, "brand_logo_data", "")
    set_setting(db, "brand_logo_mime", "")
    set_setting(db, "brand_logo_updated_at", updated_at)
    audit(db, "admin.brand_logo_reset", request, actor=admin.id, target=admin.id)
    db.commit()
    return {"message": "Logo predefinito ripristinato.", "logoUrl": f"./api/branding/logo?v={updated_at}", "logoCustomized": False}


@app.get("/manifest.webmanifest", include_in_schema=False)
def web_manifest(db: Session = Depends(get_db)) -> JSONResponse:
    settings = public_settings(db)
    payload = {
        "name": str(settings["siteName"] or "Quiz 400 VVF 2026"),
        "short_name": "Quiz 400 VVF",
        "description": "Quiz Vigili del Fuoco organizzati per materia, con correzione e statistiche.",
        "start_url": "./#home",
        "display": "standalone",
        "background_color": "#0b0b0c",
        "theme_color": "#b42318",
        "icons": [{"src": settings["logoUrl"], "sizes": "any", "type": settings["logoMime"], "purpose": "any maskable"}],
    }
    return JSONResponse(payload, media_type="application/manifest+json", headers={"Cache-Control": "no-cache"})


@app.get("/api/internal/tls-allowed")
def tls_allowed(domain: str, db: Session = Depends(get_db)) -> Response:
    allowed = {str(get_setting(db, "duckdns_domain") or "").lower().removesuffix(".duckdns.org") + ".duckdns.org"}
    public_url = str(get_setting(db, "public_url") or "")
    if urlparse(public_url).hostname:
        allowed.add(str(urlparse(public_url).hostname).lower())
    if domain.strip().lower() not in allowed or domain.strip().lower() == ".duckdns.org":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Dominio non autorizzato.")
    return Response(status_code=204)


@app.post("/api/auth/register", status_code=201)
def register(payload: PublicRegistrationInput, request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    enforce_rate_limit(request, "register", 8, 3600)
    if not get_setting(db, "registration_enabled"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Le registrazioni sono chiuse.")
    current_policy_version = str(get_setting(db, "privacy_policy_version") or "")
    if not payload.privacy_acknowledged or payload.privacy_policy_version != current_policy_version:
        raise HTTPException(status.HTTP_409_CONFLICT, "Leggi e conferma la presa visione dell'informativa privacy aggiornata.")
    try:
        username = normalize_username(payload.username)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    email = normalize_email(str(payload.email) if payload.email else None)
    if db.scalar(select(User).where((User.username == username) | ((User.email == email) if email else False))):
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome utente o email già utilizzati.")
    user = User(
        username=username,
        display_name=payload.name.strip(),
        email=email,
        password_hash=password_hasher.hash(payload.password),
        role="user",
        active=True,
        approved=False,
        privacy_policy_version=current_policy_version,
        privacy_acknowledged_at=utcnow(),
    )
    user.state = UserState(data=empty_state())
    db.add(user)
    db.flush()
    audit(db, "user.registered", request, target=user.id, privacyPolicyVersion=current_policy_version)
    db.commit()
    return {"message": "Registrazione completata. Il tuo account è in attesa di approvazione da parte dell’amministratore."}


@app.post("/api/auth/login")
def login(payload: LoginInput, request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_rate_limit(request, "login", 12, 900)
    username = payload.username.strip().lower()
    user = db.scalar(select(User).where(User.username == username))
    try:
        valid = password_hasher.verify(user.password_hash if user else DUMMY_PASSWORD_HASH, payload.password)
    except (VerifyMismatchError, InvalidHashError):
        valid = False
    if not user or not valid or not user.active:
        audit(db, "auth.login_failed", request, target=user.id if user else None, usernameHash=hashlib.sha256(username.encode("utf-8")).hexdigest()[:16])
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenziali non valide.")
    if not user.approved:
        audit(db, "auth.login_pending_approval", request, target=user.id)
        db.commit()
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account in attesa di approvazione da parte dell’amministratore.")
    if password_hasher.check_needs_rehash(user.password_hash):
        user.password_hash = password_hasher.hash(payload.password)
    user.last_login_at = utcnow()
    create_session(db, user, request, response)
    audit(db, "auth.login", request, actor=user.id, target=user.id)
    db.commit()
    return {"user": serialize_user(user, include_state=True), "config": get_setting(db, "exam_config"), "challengeGate": daily_challenge_gate_payload(user, db)}


@app.post("/api/auth/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        login_session = db.scalar(select(LoginSession).where(LoginSession.token_hash == token_hash(raw)))
        if login_session:
            db.delete(login_session)
            db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@app.get("/api/auth/me")
def me(user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return {"user": serialize_user(user, include_state=True), "config": get_setting(db, "exam_config"), "challengeGate": daily_challenge_gate_payload(user, db)}


@app.get("/api/account/data-export")
def export_personal_data(user: User = Depends(require_user), db: Session = Depends(get_db)) -> JSONResponse:
    activity = db.scalars(
        select(AuditLog)
        .where((AuditLog.actor_user_id == user.id) | (AuditLog.target_user_id == user.id))
        .order_by(AuditLog.created_at.asc())
    ).all()
    reports = db.scalars(select(QuestionReport).where(QuestionReport.user_id == user.id).order_by(QuestionReport.created_at.asc())).all()
    ratings = db.scalars(select(QuestionRating).where(QuestionRating.user_id == user.id).order_by(QuestionRating.created_at.asc())).all()
    payload = {
        "app": "Quiz 400 VVF 2026",
        "exportedAt": utcnow().isoformat(),
        "profile": serialize_user(user),
        "profilePhoto": ({"mime": user.avatar.mime, "dataUrl": f"data:{user.avatar.mime};base64,{user.avatar.data}", "updatedAt": aware_utc(user.avatar.updated_at).isoformat()} if user.avatar else None),
        "studyState": user.state.data if user.state else empty_state(),
        "questionReports": [
            {
                "questionId": row.question_id,
                "reason": row.reason,
                "note": row.note,
                "status": row.status,
                "createdAt": aware_utc(row.created_at).isoformat(),
                "reviewedAt": aware_utc(row.reviewed_at).isoformat() if row.reviewed_at else None,
            }
            for row in reports
        ],
        "questionDifficultyRatings": [
            {"questionId": row.question_id, "rating": row.rating, "createdAt": aware_utc(row.created_at).isoformat(), "updatedAt": aware_utc(row.updated_at).isoformat()}
            for row in ratings
        ],
        "activityLog": [
            {
                "action": row.action,
                "details": row.details,
                "ipAddress": row.ip_address,
                "createdAt": row.created_at.isoformat(),
            }
            for row in activity
        ],
    }
    filename = f"quiz400-miei-dati-{utcnow().date().isoformat()}.json"
    return JSONResponse(payload, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.put("/api/auth/profile")
def update_profile(payload: ProfileInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    email = normalize_email(str(payload.email) if payload.email else None)
    if email and db.scalar(select(User).where(User.email == email, User.id != user.id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email già utilizzata.")
    user.display_name = payload.name.strip()
    user.email = email
    audit(db, "user.profile_updated", request, actor=user.id, target=user.id)
    db.commit()
    return {"user": serialize_user(user, include_state=True)}


def user_avatar_response(request: Request, content: bytes, mime: str) -> Response:
    etag = f'"{hashlib.sha256(content).hexdigest()}"'
    headers = {"Cache-Control": "private, no-cache", "ETag": etag}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)
    return Response(content=content, media_type=mime, headers=headers)


@app.get("/api/users/{user_id}/avatar")
def user_avatar(user_id: str, request: Request, _: User = Depends(require_user), db: Session = Depends(get_db)) -> Response:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    avatar = db.get(UserAvatar, user_id)
    if avatar:
        try:
            content = base64.b64decode(avatar.data, validate=True)
        except (ValueError, TypeError):
            content = b""
        if content and len(content) <= MAX_AVATAR_BYTES and image_signature_matches(avatar.mime, content):
            return user_avatar_response(request, content, avatar.mime)
    return user_avatar_response(request, DEFAULT_AVATAR_BYTES, "image/jpeg")


@app.put("/api/auth/avatar")
def update_avatar(payload: ProfileAvatarInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    mime, _, encoded = decode_image_data_url(payload.data_url, MAX_AVATAR_BYTES, "La foto profilo")
    updated_at = utcnow()
    avatar = db.get(UserAvatar, user.id)
    if avatar:
        avatar.data = encoded
        avatar.mime = mime
        avatar.updated_at = updated_at
    else:
        db.add(UserAvatar(user_id=user.id, data=encoded, mime=mime, updated_at=updated_at))
    audit(db, "user.avatar_updated", request, actor=user.id, target=user.id, mime=mime)
    db.commit()
    return {"message": "Foto profilo aggiornata.", "avatarUrl": f"./api/users/{user.id}/avatar?v={int(updated_at.timestamp())}"}


@app.delete("/api/auth/avatar")
def delete_avatar(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    avatar = db.get(UserAvatar, user.id)
    if avatar:
        db.delete(avatar)
    audit(db, "user.avatar_removed", request, actor=user.id, target=user.id)
    db.commit()
    return {"message": "Foto profilo rimossa.", "avatarUrl": f"./api/users/{user.id}/avatar?v={int(utcnow().timestamp())}"}


@app.post("/api/auth/change-password", status_code=204)
def change_password(payload: ChangePasswordInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> Response:
    try:
        valid = password_hasher.verify(user.password_hash, payload.current_password)
    except (VerifyMismatchError, InvalidHashError):
        valid = False
    if not valid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password attuale non corretta.")
    user.password_hash = password_hasher.hash(payload.new_password)
    user.must_change_password = False
    db.execute(LoginSession.__table__.delete().where(LoginSession.user_id == user.id, LoginSession.token_hash != token_hash(request.cookies.get(SESSION_COOKIE, ""))))
    audit(db, "auth.password_changed", request, actor=user.id, target=user.id)
    db.commit()
    return Response(status_code=204)


@app.post("/api/auth/forgot-password", status_code=202)
async def forgot_password(payload: ForgotInput, request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    enforce_rate_limit(request, "forgot", 6, 3600)
    account = payload.account.strip().lower()
    user = db.scalar(select(User).where((User.username == account) | (User.email == account)))
    generic = "Se l'account esiste, riceverai le istruzioni. Se la posta non è configurata, contatta l'amministratore."
    if not user or not user.active or not user.email or not get_setting(db, "smtp_enabled"):
        audit(db, "auth.reset_requested", request, target=user.id if user else None, delivery=False)
        db.commit()
        return {"message": generic}
    raw = secrets.token_urlsafe(48)
    minutes = max(10, min(1440, int(get_setting(db, "reset_token_minutes") or 30)))
    db.add(PasswordReset(user_id=user.id, token_hash=token_hash(raw), expires_at=utcnow() + timedelta(minutes=minutes)))
    public_url = str(get_setting(db, "public_url") or str(request.base_url).rstrip("/"))
    link = f"{public_url}/#reset-password/{raw}"
    audit(db, "auth.reset_requested", request, target=user.id, delivery=True)
    db.commit()
    try:
        await send_email(user.email, "Reimposta la password di Quiz 400 VVF 2026", f"Ciao {user.display_name},\n\nusa questo link entro {minutes} minuti per scegliere una nuova password:\n\n{link}\n\nSe non hai richiesto tu il recupero, ignora questa email.", db)
        set_setting(db, "smtp_last_status", {"ok": True, "at": utcnow().isoformat(), "kind": "password-reset", "message": "Email di recupero consegnata al server SMTP."})
        db.commit()
    except Exception as error:
        set_setting(db, "smtp_last_status", {"ok": False, "at": utcnow().isoformat(), "kind": "password-reset", "message": str(error)[:300]})
        db.commit()
    return {"message": generic}


@app.post("/api/auth/reset-password", status_code=204)
def reset_password(payload: ResetInput, request: Request, db: Session = Depends(get_db)) -> Response:
    enforce_rate_limit(request, "reset", 10, 3600)
    reset = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == token_hash(payload.token), PasswordReset.used_at.is_(None), PasswordReset.expires_at > utcnow()))
    if not reset:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Link scaduto o non valido.")
    user = db.get(User, reset.user_id)
    if not user or not user.active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Link scaduto o non valido.")
    user.password_hash = password_hasher.hash(payload.password)
    user.must_change_password = False
    reset.used_at = utcnow()
    db.execute(LoginSession.__table__.delete().where(LoginSession.user_id == user.id))
    audit(db, "auth.password_reset", request, target=user.id)
    db.commit()
    return Response(status_code=204)


@app.put("/api/cloud/state")
def save_cloud_state(payload: StateInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, int]:
    encoded = json.dumps(payload.state, ensure_ascii=False).encode("utf-8")
    if len(encoded) > MAX_STATE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Stato utente troppo grande.")
    previous_sessions = len(user.state.data.get("sessions", [])) if user.state and isinstance(user.state.data, dict) and isinstance(user.state.data.get("sessions"), list) else 0
    if not user.state:
        user.state = UserState(data=payload.state, revision=1)
    else:
        user.state.data = payload.state
        user.state.revision += 1
        user.state.updated_at = utcnow()
    if payload.config is not None and user.role == "admin":
        set_setting(db, "exam_config", payload.config)
    current_sessions = payload.state.get("sessions", []) if isinstance(payload.state.get("sessions"), list) else []
    if len(current_sessions) > previous_sessions:
        latest = current_sessions[-1] if current_sessions and isinstance(current_sessions[-1], dict) else {}
        audit(db, "quiz.completed", request, actor=user.id, target=user.id, quizType=latest.get("type"), score=latest.get("score"), revision=user.state.revision)
    elif user.state.revision % 50 == 0:
        audit(db, "state.checkpoint", request, actor=user.id, target=user.id, revision=user.state.revision)
    db.commit()
    return {"revision": user.state.revision}


@app.get("/api/questions/availability")
def question_availability(_: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(DisabledQuestion).order_by(DisabledQuestion.disabled_at)).all()
    latest = max((aware_utc(row.disabled_at) for row in rows), default=None)
    return {
        "disabledQuestionIds": [row.question_id for row in rows],
        "revision": f"{len(rows)}:{latest.isoformat() if latest else '0'}",
    }


def question_rating_payload(question_id: str, user_id: str, db: Session) -> dict[str, Any]:
    count, average = db.execute(
        select(func.count(QuestionRating.id), func.avg(QuestionRating.rating))
        .where(QuestionRating.question_id == question_id)
    ).one()
    own = db.scalar(select(QuestionRating).where(
        QuestionRating.question_id == question_id, QuestionRating.user_id == user_id
    ))
    return {
        "questionId": question_id,
        "average": round(float(average), 2) if average is not None else None,
        "count": int(count or 0),
        "userRating": own.rating if own else None,
    }


@app.get("/api/question-ratings")
def question_ratings(question_ids: str = "", user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    ids = list(dict.fromkeys(item.strip() for item in question_ids.split(",") if item.strip()))
    if not ids or len(ids) > 100 or any(len(item) > 100 for item in ids):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Richiedi da 1 a 100 quesiti validi.")
    if any(item not in questions_by_id for item in ids):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quesito non trovato.")
    return {"ratings": [question_rating_payload(item, user.id, db) for item in ids]}


@app.put("/api/question-ratings/{question_id}")
def rate_question(question_id: str, payload: QuestionRatingInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_rate_limit(request, "question-rating", 300, 3600)
    question_id = str(question_id).strip()
    if question_id not in questions_by_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quesito non trovato.")
    if db.get(DisabledQuestion, question_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Il quesito non è più disponibile.")
    row = db.scalar(select(QuestionRating).where(
        QuestionRating.question_id == question_id, QuestionRating.user_id == user.id
    ))
    if row:
        row.rating = payload.rating
        row.updated_at = utcnow()
    else:
        db.add(QuestionRating(question_id=question_id, user_id=user.id, rating=payload.rating))
    audit(db, "question.difficulty_rated", request, actor=user.id, target=user.id, questionId=question_id, rating=payload.rating)
    db.commit()
    return {"rating": question_rating_payload(question_id, user.id, db), "message": "Valutazione aggiornata."}


@app.post("/api/question-reports", status_code=201)
def create_question_report(payload: QuestionReportInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> JSONResponse:
    enforce_rate_limit(request, "question-report", 30, 3600)
    question_id = str(payload.question_id).strip()
    if question_id not in questions_by_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quesito non trovato.")
    if db.get(DisabledQuestion, question_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Il quesito è già stato reso non disponibile dall'amministratore.")
    existing = db.scalar(select(QuestionReport).where(QuestionReport.question_id == question_id, QuestionReport.user_id == user.id, QuestionReport.status == "pending"))
    if existing:
        return JSONResponse({"report": serialize_question_report(existing, db), "duplicate": True, "message": "Avevi già segnalato questo quesito: la revisione è in attesa."}, status_code=200)
    report = QuestionReport(question_id=question_id, user_id=user.id, reason=payload.reason, note=payload.note.strip(), status="pending")
    db.add(report)
    db.flush()
    audit(db, "question.reported", request, actor=user.id, target=user.id, questionId=question_id, reason=payload.reason)
    db.commit()
    return JSONResponse({"report": serialize_question_report(report, db), "duplicate": False, "message": "Segnalazione inviata all'amministratore."}, status_code=201)


@app.get("/api/question-reports/replies")
def question_report_replies(user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(QuestionReport).where(
        QuestionReport.user_id == user.id, QuestionReport.status != "pending",
        QuestionReport.reply.is_not(None), QuestionReport.reply_read_at.is_(None),
    ).order_by(QuestionReport.reviewed_at.asc()).limit(20)).all()
    return {"replies": [serialize_question_report(row, db) for row in rows]}


@app.post("/api/question-reports/{report_id}/read")
def read_question_report_reply(report_id: str, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, bool]:
    row = db.get(QuestionReport, report_id)
    if not row or row.user_id != user.id or row.reply is None or row.status == "pending":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Risposta non trovata.")
    if row.reply_read_at is None:
        row.reply_read_at = utcnow()
        db.commit()
    return {"ok": True}


@app.get("/api/admin/question-reports")
def admin_question_reports(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    pending = db.scalars(select(QuestionReport).where(QuestionReport.status == "pending").order_by(QuestionReport.created_at.desc())).all()
    disabled = db.scalars(select(DisabledQuestion).order_by(DisabledQuestion.disabled_at.desc())).all()
    return {
        "pendingCount": len(pending),
        "pending": [serialize_question_report(row, db) for row in pending],
        "disabled": [serialize_disabled_question(row, db) for row in disabled],
    }


@app.post("/api/admin/question-reports/{report_id}/dismiss")
def dismiss_question_report(report_id: str, request: Request, payload: QuestionReportReplyInput = QuestionReportReplyInput(), admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    report = db.get(QuestionReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Segnalazione non trovata.")
    if report.status == "pending":
        report.status = "dismissed"
        report.reply = payload.reply.strip() or "Il quesito è stato verificato e risulta corretto. Consulta la risposta corretta e la spiegazione riportate qui sotto."
        report.reply_read_at = None
        report.reviewed_at = utcnow()
        report.reviewed_by_user_id = admin.id
        audit(db, "admin.question_report_dismissed", request, actor=admin.id, target=report.user_id, questionId=report.question_id, reportId=report.id)
        db.commit()
    return {"report": serialize_question_report(report, db), "message": "Segnalazione chiusa: il quesito resta disponibile."}


@app.post("/api/admin/questions/{question_id}/disable")
def disable_question(question_id: str, payload: QuestionModerationInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    question_id = str(question_id).strip()
    if question_id not in questions_by_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quesito non trovato.")
    row = db.get(DisabledQuestion, question_id)
    if not row:
        row = DisabledQuestion(question_id=question_id)
        db.add(row)
    row.reason = payload.reason.strip() or "Quesito disattivato dopo revisione amministrativa."
    row.disabled_at = utcnow()
    row.disabled_by_user_id = admin.id
    reports = db.scalars(select(QuestionReport).where(QuestionReport.question_id == question_id, QuestionReport.status == "pending")).all()
    for report in reports:
        report.status = "resolved"
        report.reply = payload.reply.strip() or "La tua segnalazione è stata accolta: il quesito è stato escluso dalle nuove esercitazioni. Grazie per il tuo contributo."
        report.reply_read_at = None
        report.reviewed_at = row.disabled_at
        report.reviewed_by_user_id = admin.id
    audit(db, "admin.question_disabled", request, actor=admin.id, target=admin.id, questionId=question_id, reportsResolved=len(reports))
    db.commit()
    return {
        "disabled": serialize_disabled_question(row, db),
        "reportsResolved": len(reports),
        "currentChallengesPreserved": True,
        "message": "Quesito disattivato per tutte le nuove esercitazioni. Le prove e le classifiche già create restano invariate.",
    }


@app.delete("/api/admin/questions/{question_id}/disable")
def enable_question(question_id: str, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    row = db.get(DisabledQuestion, str(question_id))
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Il quesito è già disponibile.")
    db.delete(row)
    audit(db, "admin.question_enabled", request, actor=admin.id, target=admin.id, questionId=str(question_id))
    db.commit()
    return {"message": "Quesito riattivato nelle nuove esercitazioni."}


def parsed_challenge_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sfida non trovata.") from error


def user_challenge_attempt(db: Session, challenge_date: date, user_id: str, lock: bool = False) -> DailyChallengeAttempt | None:
    query = select(DailyChallengeAttempt).where(DailyChallengeAttempt.challenge_date == challenge_date, DailyChallengeAttempt.user_id == user_id)
    if lock:
        query = query.with_for_update()
    return db.scalar(query)


@app.get("/api/challenges/today")
def today_challenge(user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not get_setting(db, "daily_challenge_enabled"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La Sfida del giorno è disattivata.")
    challenge = get_or_create_daily_challenge(challenge_today(), db)
    db.commit()
    attempt = user_challenge_attempt(db, challenge.challenge_date, user.id)
    return serialize_daily_challenge(challenge, attempt, db, user)


@app.post("/api/challenges/today/start")
def start_today_challenge(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not get_setting(db, "daily_challenge_enabled"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La Sfida del giorno è disattivata.")
    challenge = get_or_create_daily_challenge(challenge_today(), db)
    attempt = user_challenge_attempt(db, challenge.challenge_date, user.id)
    if not attempt:
        attempt = DailyChallengeAttempt(challenge_date=challenge.challenge_date, user_id=user.id, answers=[None] * len(challenge.question_ids), question_seconds=[0] * len(challenge.question_ids))
        db.add(attempt)
        try:
            db.flush()
            audit(db, "challenge.started", request, actor=user.id, target=user.id, challengeDate=challenge.challenge_date.isoformat())
            db.commit()
        except IntegrityError:
            db.rollback()
            attempt = user_challenge_attempt(db, challenge.challenge_date, user.id)
            if not attempt:
                raise
    else:
        db.commit()
    return serialize_daily_challenge(challenge, attempt, db, user)


@app.put("/api/challenges/{challenge_date}/answers")
def save_challenge_answers(challenge_date: str, payload: DailyChallengeAnswersInput, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    selected_date = parsed_challenge_date(challenge_date)
    challenge = db.get(DailyChallenge, selected_date)
    attempt = user_challenge_attempt(db, selected_date, user.id, lock=True)
    if not challenge or not attempt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sfida non trovata o non ancora iniziata.")
    if attempt.submitted_at or utcnow() >= challenge_expiry(attempt):
        if not attempt.submitted_at:
            finalize_challenge_attempt(attempt, challenge, challenge_expiry(attempt))
            record_challenge_in_user_state(user, attempt, challenge)
            db.commit()
        return serialize_daily_challenge(challenge, attempt, db, user)
    attempt.answers = validate_challenge_answers(challenge, payload.answers)
    question_seconds = validate_challenge_question_seconds(payload.questionSeconds, len(challenge.question_ids))
    if question_seconds is not None:
        attempt.question_seconds = question_seconds
    db.commit()
    return {
        "status": "active",
        "date": selected_date.isoformat(),
        "remainingSeconds": max(0, int((challenge_expiry(attempt) - utcnow()).total_seconds())),
        "answered": sum(1 for answer in attempt.answers if answer is not None),
    }


@app.post("/api/challenges/{challenge_date}/submit")
def submit_challenge(challenge_date: str, payload: DailyChallengeAnswersInput, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    selected_date = parsed_challenge_date(challenge_date)
    challenge = db.get(DailyChallenge, selected_date)
    attempt = user_challenge_attempt(db, selected_date, user.id, lock=True)
    if not challenge or not attempt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sfida non trovata o non ancora iniziata.")
    if not attempt.submitted_at:
        now = utcnow()
        question_seconds = validate_challenge_question_seconds(payload.questionSeconds, len(challenge.question_ids))
        if question_seconds is not None:
            attempt.question_seconds = question_seconds
        if now < challenge_expiry(attempt):
            attempt.answers = validate_challenge_answers(challenge, payload.answers)
            finalize_challenge_attempt(attempt, challenge, now)
        else:
            finalize_challenge_attempt(attempt, challenge, challenge_expiry(attempt))
        record_challenge_in_user_state(user, attempt, challenge)
        audit(db, "challenge.completed", request, actor=user.id, target=user.id, challengeDate=selected_date.isoformat(), score=challenge_score(attempt))
        db.commit()
    return serialize_daily_challenge(challenge, attempt, db, user)


@app.get("/api/challenges/{challenge_date}/leaderboard")
def daily_challenge_leaderboard(challenge_date: str, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    selected_date = parsed_challenge_date(challenge_date)
    if not db.get(DailyChallenge, selected_date):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sfida non trovata.")
    return challenge_leaderboard(db, selected_date, user.id, user.role in {"admin", "moderator"})


@app.get("/api/admin/challenges/{challenge_date}/attempts/{attempt_id}")
def admin_daily_challenge_attempt(challenge_date: str, attempt_id: str, _: User = Depends(require_dashboard_reader), db: Session = Depends(get_db)) -> dict[str, Any]:
    selected_date = parsed_challenge_date(challenge_date)
    challenge = db.get(DailyChallenge, selected_date)
    attempt = db.get(DailyChallengeAttempt, attempt_id)
    if not challenge or not attempt or attempt.challenge_date != selected_date or not attempt.submitted_at:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prova completata non trovata.")
    participant = db.get(User, attempt.user_id)
    if not participant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente della prova non trovato.")
    return {
        "attemptId": attempt.id,
        "date": selected_date.isoformat(),
        "participant": {"name": participant.display_name, "username": participant.username, "avatarUrl": f"./api/users/{participant.id}/avatar"},
        "result": {
            "correct": attempt.correct,
            "wrong": attempt.wrong,
            "blank": attempt.blank,
            "score": challenge_score(attempt),
            "durationSeconds": attempt.duration_seconds,
            "submittedAt": aware_utc(attempt.submitted_at).isoformat(),
            "questions": challenge_result_details(attempt, challenge),
        },
    }


@app.get("/api/admin/users")
def admin_users(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(User).order_by(User.created_at.desc())).all()
    users_payload = []
    for row in rows:
        item = serialize_user(row)
        item["statistics"] = state_statistics(row.state.data if row.state else {})
        item["stateUpdatedAt"] = row.state.updated_at.isoformat() if row.state else None
        users_payload.append(item)
    forty_count = sum(item["statistics"]["fortyQuizzes"] for item in users_payload)
    subject_count = sum(item["statistics"]["subjectQuizzes"] for item in users_payload)
    forty_score_total = sum((item["statistics"]["averageFortyScore"] or 0) * item["statistics"]["fortyQuizzes"] for item in users_payload)
    subject_accuracy_total = sum((item["statistics"]["averageSubjectAccuracy"] or 0) * item["statistics"]["subjectQuizzes"] for item in users_payload)
    totals = {
        "users": len(rows),
        "active": sum(1 for row in rows if row.active),
        "pendingApproval": sum(1 for row in rows if not row.approved),
        "admins": sum(1 for row in rows if row.role == "admin"),
        "moderators": sum(1 for row in rows if row.role == "moderator"),
        "simulations": sum(item["statistics"]["simulations"] for item in users_payload),
        "fortyQuizzes": forty_count,
        "subjectQuizzes": subject_count,
        "averageFortyScore": round(forty_score_total / forty_count, 2) if forty_count else None,
        "averageSubjectAccuracy": round(subject_accuracy_total / subject_count, 1) if subject_count else None,
    }
    return {"users": users_payload, "totals": totals}


@app.get("/api/admin/users/pending-count")
def admin_pending_users_count(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, int]:
    pending_count = db.scalar(select(func.count()).select_from(User).where(User.approved.is_(False))) or 0
    return {"pendingCount": int(pending_count)}


def session_category_rows(session: dict[str, Any]) -> list[tuple[str, float, float, float]]:
    payload = session.get("perCategory")
    if not isinstance(payload, dict):
        return []
    rows: list[tuple[str, float, float, float]] = []
    for category, values in payload.items():
        if not isinstance(values, dict):
            continue
        correct = numeric_value(values.get("correct")) or 0
        wrong = numeric_value(values.get("wrong")) or 0
        blank = numeric_value(values.get("blank")) or 0
        rows.append((macro_question_category(category), correct, wrong, blank))
    return rows


@app.get("/api/admin/dashboard")
def admin_population_dashboard(_: User = Depends(require_dashboard_reader), db: Session = Depends(get_db)) -> dict[str, Any]:
    theoretical_cutoff = round(float(get_setting(db, "theoretical_cutoff")), 2)
    candidates = db.scalars(select(User).where(User.active.is_(True), User.approved.is_(True))).all()
    attempts: list[dict[str, Any]] = []
    candidate_scores: list[dict[str, Any]] = []
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_category: dict[str, dict[str, float]] = defaultdict(lambda: {"correct": 0, "wrong": 0, "blank": 0, "attempts": 0})
    by_day: dict[str, list[float]] = defaultdict(list)
    for candidate in candidates:
        state_data = candidate.state.data if candidate.state and isinstance(candidate.state.data, dict) else {}
        sessions = state_data.get("sessions", []) if isinstance(state_data.get("sessions"), list) else []
        rows: list[dict[str, Any]] = []
        for session in sessions:
            if not isinstance(session, dict) or session.get("type") != "daily-challenge":
                continue
            score = session_score(session)
            if score is None:
                continue
            correct = numeric_value(session.get("correct")) or 0
            wrong = numeric_value(session.get("wrong")) or 0
            blank = numeric_value(session.get("blank")) or max(0, 40 - correct - wrong)
            row = {"score": score, "correct": correct, "wrong": wrong, "blank": blank, "type": str(session.get("type"))}
            rows.append(row)
            attempts.append(row)
            by_type[row["type"]].append(row)
            at = str(session.get("at") or "")[:10]
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", at):
                by_day[at].append(score)
            for category, cat_correct, cat_wrong, cat_blank in session_category_rows(session):
                item = by_category[category]
                item["correct"] += cat_correct
                item["wrong"] += cat_wrong
                item["blank"] += cat_blank
                item["attempts"] += 1
        if rows:
            candidate_scores.append({"id": candidate.id, "name": candidate.display_name, "username": candidate.username, "role": candidate.role, "avatarUrl": f"./api/users/{candidate.id}/avatar", "attempts": len(rows), "average": sum(item["score"] for item in rows) / len(rows)})

    reliable = [item for item in candidate_scores if item["attempts"] >= 3]
    band_defs = [("Molto preparati · 32–40", 32, 41), ("Buona preparazione · 28–31,99", 28, 32), ("In consolidamento · 24–27,99", 24, 28), ("Da rafforzare · meno di 24", -100, 24)]
    bands = []
    for label, low, high in band_defs:
        members = sorted((item for item in candidate_scores if low <= item["average"] < high), key=lambda item: item["average"], reverse=True)
        bands.append({"label": label, "count": len(members), "candidates": [{"id": item["id"], "name": item["name"], "username": item["username"], "role": item["role"], "avatarUrl": item["avatarUrl"], "averageScore": round(item["average"], 2), "attempts": item["attempts"]} for item in members]})
    type_labels = {"daily-challenge": "Sfide del giorno"}
    type_stats = [{"type": key, "label": type_labels[key], **session_group_statistics(by_type.get(key, []))} for key in type_labels]
    categories = []
    for category, values in by_category.items():
        answered = values["correct"] + values["wrong"]
        total = answered + values["blank"]
        categories.append({"category": category, "attempts": int(values["attempts"]), "accuracy": round(values["correct"] / answered * 100, 1) if answered else None, "correctRate": round(values["correct"] / total * 100, 1) if total else None})
    categories.sort(key=lambda item: (item["accuracy"] is None, item["accuracy"] or 0))
    today = challenge_today()
    trend = []
    for offset in range(13, -1, -1):
        day = (today - timedelta(days=offset)).isoformat()
        scores = by_day.get(day, [])
        trend.append({"date": day, "attempts": len(scores), "averageScore": average(scores)})
    confidence = "alta" if len(reliable) >= 30 and len(attempts) >= 100 else "media" if len(reliable) >= 10 and len(attempts) >= 30 else "bassa"
    avg = lambda key: average([float(item[key]) for item in attempts], 1)
    return {
        "generatedAt": utcnow().isoformat(),
        "summary": {"eligibleCandidates": len(candidates), "participants": len(candidate_scores), "reliableCandidates": len(reliable), "attempts": len(attempts), "averageAttemptScore": average([item["score"] for item in attempts]), "averageCandidateScore": average([item["average"] for item in candidate_scores]), "reliableAverageScore": average([item["average"] for item in reliable]), "averageCorrect": avg("correct"), "averageWrong": avg("wrong"), "averageBlank": avg("blank"), "confidence": confidence, "theoreticalCutoff": theoretical_cutoff, "candidatesAboveCutoff": sum(1 for item in candidate_scores if item["average"] >= theoretical_cutoff), "candidatesBelowCutoff": sum(1 for item in candidate_scores if item["average"] < theoretical_cutoff)},
        "bands": bands,
        "types": type_stats,
        "categories": categories,
        "trend": trend,
    }


@app.put("/api/admin/dashboard/settings")
def save_dashboard_settings(payload: DashboardSettingsInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    value = round(payload.theoretical_cutoff, 2)
    set_setting(db, "theoretical_cutoff", value)
    audit(db, "admin.dashboard_settings_updated", request, actor=admin.id, target=admin.id, theoreticalCutoff=value)
    db.commit()
    return {"theoreticalCutoff": value}


@app.get("/api/admin/dashboard/candidates/{user_id}/challenges")
def admin_candidate_challenges(user_id: str, _: User = Depends(require_dashboard_reader), db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    attempts = db.scalars(
        select(DailyChallengeAttempt)
        .where(DailyChallengeAttempt.user_id == user_id, DailyChallengeAttempt.submitted_at.is_not(None))
        .order_by(DailyChallengeAttempt.challenge_date.desc())
    ).all()
    return {
        "candidate": {"id": target.id, "name": target.display_name, "username": target.username, "avatarUrl": f"./api/users/{target.id}/avatar"},
        "attempts": [{
            "id": attempt.id,
            "date": attempt.challenge_date.isoformat(),
            "score": challenge_score(attempt),
            "correct": attempt.correct,
            "wrong": attempt.wrong,
            "blank": attempt.blank,
            "durationSeconds": attempt.duration_seconds,
            "timedOut": aware_utc(attempt.submitted_at) == challenge_expiry(attempt),
        } for attempt in attempts],
    }


@app.delete("/api/admin/dashboard/challenges/{attempt_id}")
def delete_candidate_challenge(attempt_id: str, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> Response:
    attempt = db.get(DailyChallengeAttempt, attempt_id)
    if not attempt or not attempt.submitted_at:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prova giornaliera conclusa non trovata.")
    target = db.get(User, attempt.user_id)
    challenge = db.get(DailyChallenge, attempt.challenge_date)
    if not target or not challenge:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dati della prova non trovati.")
    state_data = dict(target.state.data if target.state and isinstance(target.state.data, dict) else empty_state())
    key = attempt.challenge_date.isoformat()
    state_data["sessions"] = [item for item in list(state_data.get("sessions") or []) if not (isinstance(item, dict) and item.get("type") == "daily-challenge" and item.get("challengeDate") == key)]
    state_data["dailyChallengeRecordedDates"] = [value for value in list(state_data.get("dailyChallengeRecordedDates") or []) if value != key]
    progress = dict(state_data.get("progress") or {})
    for answer, question in zip(list(attempt.answers or []), challenge_questions(challenge), strict=False):
        question_id = str(question["id"])
        item = dict(progress.get(question_id) or {})
        if not item:
            continue
        if answer is None:
            item["skipped"] = max(0, int(item.get("skipped", 0) or 0) - 1)
        else:
            item["attempts"] = max(0, int(item.get("attempts", 0) or 0) - 1)
            field = "correct" if answer == int(question["correct"]) else "wrong"
            item[field] = max(0, int(item.get(field, 0) or 0) - 1)
        attempts_left = int(item.get("attempts", 0) or 0)
        item["status"] = "unanswered" if attempts_left == 0 else "review" if int(item.get("wrong", 0) or 0) > 0 else "known"
        progress[question_id] = item
    state_data["progress"] = progress
    if target.state:
        target.state.data = state_data
        target.state.revision += 1
        target.state.updated_at = utcnow()
    audit(db, "admin.daily_challenge_deleted", request, actor=admin.id, target=target.id, attemptId=attempt.id, challengeDate=key, score=challenge_score(attempt))
    db.delete(attempt)
    db.commit()
    return Response(status_code=204)


@app.get("/api/admin/users/{user_id}/statistics")
def admin_user_statistics(user_id: str, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    state_data = target.state.data if target.state else {}
    sessions = state_data.get("sessions", []) if isinstance(state_data, dict) else []
    recent_activity = db.scalars(select(AuditLog).where(AuditLog.target_user_id == user_id).order_by(AuditLog.created_at.desc()).limit(50)).all()
    return {
        "user": serialize_user(target),
        "summary": state_statistics(state_data),
        "categories": category_statistics(state_data),
        "recentSessions": list(reversed(sessions[-50:])) if isinstance(sessions, list) else [],
        "activity": [{"action": row.action, "at": row.created_at.isoformat(), "details": row.details} for row in recent_activity],
    }


@app.post("/api/admin/users", status_code=201)
def admin_create_user(payload: AdminUserInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        username = normalize_username(payload.username)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    email = normalize_email(str(payload.email) if payload.email else None)
    if db.scalar(select(User).where((User.username == username) | ((User.email == email) if email else False))):
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome utente o email già utilizzati.")
    user = User(username=username, display_name=payload.name.strip(), email=email, password_hash=password_hasher.hash(payload.password), role=payload.role, active=True, approved=True, must_change_password=True)
    user.state = UserState(data=empty_state())
    db.add(user)
    db.flush()
    audit(db, "admin.user_created", request, actor=admin.id, target=user.id, role=user.role)
    db.commit()
    return {"user": serialize_user(user)}


@app.patch("/api/admin/users/{user_id}")
def admin_patch_user(user_id: str, payload: AdminUserPatch, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    if payload.name is not None:
        target.display_name = payload.name.strip()
    if "email" in payload.model_fields_set:
        email = normalize_email(str(payload.email) if payload.email else None)
        if email and db.scalar(select(User).where(User.email == email, User.id != target.id)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email già utilizzata.")
        target.email = email
    if payload.role is not None:
        if payload.role not in {"user", "moderator", "admin"}:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Ruolo non valido.")
        if target.role == "admin" and payload.role != "admin" and db.scalar(select(func.count(User.id)).where(User.role == "admin", User.active.is_(True))) <= 1:
            raise HTTPException(status.HTTP_409_CONFLICT, "Deve rimanere almeno un amministratore attivo.")
        target.role = payload.role
    if payload.active is not None:
        if target.id == admin.id and not payload.active:
            raise HTTPException(status.HTTP_409_CONFLICT, "Non puoi disattivare il tuo account.")
        if target.role == "admin" and not payload.active and db.scalar(select(func.count(User.id)).where(User.role == "admin", User.active.is_(True))) <= 1:
            raise HTTPException(status.HTTP_409_CONFLICT, "Deve rimanere almeno un amministratore attivo.")
        target.active = payload.active
        if not target.active:
            db.execute(LoginSession.__table__.delete().where(LoginSession.user_id == target.id))
    if payload.approved is not None:
        if target.role == "admin" and not payload.approved:
            raise HTTPException(status.HTTP_409_CONFLICT, "Un amministratore non può essere messo in attesa di approvazione.")
        target.approved = payload.approved
        if not target.approved:
            db.execute(LoginSession.__table__.delete().where(LoginSession.user_id == target.id))
    audit(db, "admin.user_updated", request, actor=admin.id, target=target.id, fields=list(payload.model_fields_set))
    db.commit()
    return {"user": serialize_user(target)}


def temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(16))


@app.post("/api/admin/users/{user_id}/reset-password")
def admin_reset_password(user_id: str, payload: AdminResetInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, str]:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    password = payload.password or temporary_password()
    target.password_hash = password_hasher.hash(password)
    target.must_change_password = True
    db.execute(LoginSession.__table__.delete().where(LoginSession.user_id == target.id))
    audit(db, "admin.password_reset", request, actor=admin.id, target=target.id)
    db.commit()
    return {"temporaryPassword": password}


@app.delete("/api/admin/users/{user_id}", status_code=204)
def admin_delete_user(user_id: str, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> Response:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato.")
    if target.id == admin.id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Non puoi eliminare il tuo account.")
    if target.role == "admin" and db.scalar(select(func.count(User.id)).where(User.role == "admin", User.active.is_(True))) <= 1:
        raise HTTPException(status.HTTP_409_CONFLICT, "Deve rimanere almeno un amministratore attivo.")
    audit(db, "admin.user_deleted", request, actor=admin.id, target=target.id)
    db.delete(target)
    db.commit()
    return Response(status_code=204)


@app.get("/api/admin/settings")
def admin_settings(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "siteName": get_setting(db, "site_name"),
        "registrationEnabled": bool(get_setting(db, "registration_enabled")),
        "dailyChallengeEnabled": bool(get_setting(db, "daily_challenge_enabled")),
        "dailyChallengeRequired": bool(get_setting(db, "daily_challenge_required")),
        "theoreticalCutoff": float(get_setting(db, "theoretical_cutoff")),
        "dailyChallengeConfig": normalized_challenge_composition(db),
        "publicUrl": get_setting(db, "public_url"),
        "sessionDays": get_setting(db, "session_days"),
        "resetTokenMinutes": get_setting(db, "reset_token_minutes"),
        "privacyNotice": get_setting(db, "privacy_notice"),
        "privacyControllerName": get_setting(db, "privacy_controller_name"),
        "privacyControllerAddress": get_setting(db, "privacy_controller_address"),
        "privacyContactEmail": get_setting(db, "privacy_contact_email"),
        "privacyPecEmail": get_setting(db, "privacy_pec_email"),
        "privacyDpoContact": get_setting(db, "privacy_dpo_contact"),
        "privacyHostingLocation": get_setting(db, "privacy_hosting_location"),
        "privacyEmailProvider": get_setting(db, "privacy_email_provider"),
        "privacyTransferNote": get_setting(db, "privacy_transfer_note"),
        "privacyPolicyVersion": get_setting(db, "privacy_policy_version"),
        "privacyEffectiveDate": get_setting(db, "privacy_effective_date"),
        "privacyAuditLogDays": get_setting(db, "privacy_audit_log_days"),
        "privacyBackupDays": get_setting(db, "privacy_backup_days"),
        "privacyComplete": public_settings(db)["privacy"]["complete"],
        "duckdnsEnabled": bool(get_setting(db, "duckdns_enabled")),
        "duckdnsDomain": get_setting(db, "duckdns_domain"),
        "duckdnsTokenConfigured": bool(get_setting(db, "duckdns_token")),
        "duckdnsIntervalMinutes": get_setting(db, "duckdns_interval_minutes"),
        "duckdnsLastStatus": get_setting(db, "duckdns_last_status"),
        "smtpEnabled": bool(get_setting(db, "smtp_enabled")),
        "smtpHost": get_setting(db, "smtp_host"),
        "smtpPort": get_setting(db, "smtp_port"),
        "smtpUsername": get_setting(db, "smtp_username"),
        "smtpPasswordConfigured": bool(get_setting(db, "smtp_password")),
        "smtpFromEmail": get_setting(db, "smtp_from_email"),
        "smtpUseTls": bool(get_setting(db, "smtp_use_tls")),
        "smtpLastStatus": get_setting(db, "smtp_last_status"),
        "logoUrl": public_settings(db)["logoUrl"],
        "logoCustomized": bool(get_setting(db, "brand_logo_data")),
        "deploymentProxyMode": DEPLOYMENT_PROXY_MODE,
        "deploymentAppPort": DEPLOYMENT_APP_PORT,
        "deploymentBindAddress": DEPLOYMENT_BIND_ADDRESS,
        "deploymentHttpPort": DEPLOYMENT_HTTP_PORT,
        "deploymentHttpsPort": DEPLOYMENT_HTTPS_PORT,
        "portControl": port_control_status(),
    }


@app.post("/api/admin/network/apply", status_code=202)
def request_port_change(payload: PortChangeInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not PORT_CONTROL_DIR:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Il controllo porte dal pannello non è installato su questo server.")
    if DEPLOYMENT_PROXY_MODE != "external":
        raise HTTPException(status.HTTP_409_CONFLICT, "Il cambio dal pannello è disponibile soltanto con il reverse proxy esterno configurato.")
    if payload.app_port == DEPLOYMENT_APP_PORT:
        raise HTTPException(status.HTTP_409_CONFLICT, "Questa è già la porta backend attiva.")
    public_url = str(get_setting(db, "public_url") or "")
    domain = (urlparse(public_url).hostname or "").lower()
    if not domain or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", domain):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Salva prima un URL pubblico valido nelle impostazioni Cloud.")
    request_id = str(uuid.uuid4())
    control_request = {
        "requestId": request_id,
        "requestedAt": utcnow().isoformat(),
        "requestedBy": admin.id,
        "currentPort": DEPLOYMENT_APP_PORT,
        "appPort": payload.app_port,
        "domain": domain,
    }
    try:
        PORT_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
        destination = PORT_CONTROL_DIR / "request.json"
        temporary = PORT_CONTROL_DIR / f"request-{request_id}.tmp"
        temporary.write_text(json.dumps(control_request, ensure_ascii=False), encoding="utf-8")
        temporary.replace(destination)
    except OSError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Impossibile comunicare con il controllo porte del server.") from error
    audit(db, "admin.port_change_requested", request, actor=admin.id, target=admin.id, oldPort=DEPLOYMENT_APP_PORT, newPort=payload.app_port)
    db.commit()
    return {"message": "Cambio porta richiesto. Il portale verrà riavviato per pochi secondi.", "requestId": request_id, "port": payload.app_port}


@app.get("/api/admin/update/status")
def update_status(_: User = Depends(require_admin)) -> dict[str, Any]:
    return {
        "currentVersion": APP_VERSION,
        "repository": UPDATE_REPOSITORY,
        "assetName": UPDATE_ASSET_NAME,
        "database": "PostgreSQL",
        "control": portal_control_status(),
        "github": public_update_metadata(read_control_json("github-release.json")),
        "upload": public_update_metadata(read_control_json("pending-update.json")),
    }


@app.post("/api/admin/update/check")
async def check_github_update(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", UPDATE_REPOSITORY):
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Repository aggiornamenti non configurato correttamente.")
    api_url = f"https://api.github.com/repos/{UPDATE_REPOSITORY}/releases/latest"
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers={"Accept": "application/vnd.github+json", "User-Agent": f"Quiz400VVF/{APP_VERSION}"}) as client:
            response = await client.get(api_url)
            response.raise_for_status()
        release = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "GitHub non è raggiungibile oppure non ha una release pubblicata.") from error
    latest_version = str(release.get("tag_name") or "").strip().removeprefix("v")
    if not semantic_version(latest_version):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "La release GitHub non contiene una versione valida.")
    assets = release.get("assets") if isinstance(release.get("assets"), list) else []
    asset = next((item for item in assets if item.get("name") == UPDATE_ASSET_NAME), None)
    if not asset:
        asset = next((item for item in assets if str(item.get("name", "")).lower().endswith("server.zip")), None)
    asset_url = str(asset.get("browser_download_url") or "") if asset else ""
    expected_prefix = f"https://github.com/{UPDATE_REPOSITORY}/releases/download/"
    if asset_url and not asset_url.startswith(expected_prefix):
        asset_url = ""
    current_semver = semantic_version(APP_VERSION) or (0, 0, 0)
    latest_semver = semantic_version(latest_version) or (0, 0, 0)
    metadata = {
        "source": "github",
        "currentVersion": APP_VERSION,
        "latestVersion": latest_version,
        "updateAvailable": latest_semver > current_semver,
        "canInstall": latest_semver > current_semver and bool(asset_url),
        "changelog": str(release.get("body") or "Nessun changelog pubblicato.")[:20000],
        "releaseUrl": str(release.get("html_url") or ""),
        "publishedAt": release.get("published_at"),
        "checkedAt": utcnow().isoformat(),
        "assetName": str(asset.get("name") or "") if asset else "",
        "assetSize": int(asset.get("size") or 0) if asset else 0,
        "assetUrl": asset_url,
    }
    write_control_json("github-release.json", metadata)
    audit(db, "admin.update_checked", request, actor=admin.id, target=admin.id, latestVersion=latest_version, updateAvailable=metadata["updateAvailable"])
    db.commit()
    return public_update_metadata(metadata) or {}


@app.post("/api/admin/update/upload", status_code=201)
async def upload_update_package(request: Request, file: UploadFile = File(...), admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not PORT_CONTROL_DIR:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Installa prima il controllo aggiornamenti sul server.")
    if not str(file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Carica il file ZIP server prodotto per una release.")
    uploads_dir = PORT_CONTROL_DIR / "uploads"
    try:
        uploads_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "La cartella degli aggiornamenti non è scrivibile.") from error
    package_id = str(uuid.uuid4())
    destination = uploads_dir / f"update-{package_id}.zip"
    temporary = uploads_dir / f".update-{package_id}.tmp"
    size = 0
    digest = hashlib.sha256()
    try:
        with temporary.open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPDATE_BYTES:
                    raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Il pacchetto supera 96 MB.")
                digest.update(chunk)
                handle.write(chunk)
        temporary.replace(destination)
        inspected = inspect_update_archive(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    latest_semver = semantic_version(inspected["version"]) or (0, 0, 0)
    current_semver = semantic_version(APP_VERSION) or (0, 0, 0)
    metadata = {
        "source": "upload",
        "currentVersion": APP_VERSION,
        "latestVersion": inspected["version"],
        "updateAvailable": latest_semver > current_semver,
        "canInstall": latest_semver > current_semver,
        "changelog": inspected["changelog"] or "Nessun changelog incluso nel pacchetto.",
        "platform": inspected["platform"],
        "uploadedAt": utcnow().isoformat(),
        "originalName": Path(str(file.filename)).name[:200],
        "assetSize": size,
        "sha256": digest.hexdigest(),
        "filePath": f"uploads/{destination.name}",
    }
    write_control_json("pending-update.json", metadata)
    audit(db, "admin.update_uploaded", request, actor=admin.id, target=admin.id, version=inspected["version"], size=size)
    db.commit()
    return public_update_metadata(metadata) or {}


@app.post("/api/admin/update/install", status_code=202)
def install_update(payload: UpdateInstallInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    source_file = "github-release.json" if payload.source == "github" else "pending-update.json"
    metadata = read_control_json(source_file)
    if not metadata:
        raise HTTPException(status.HTTP_409_CONFLICT, "Prima controlla GitHub oppure carica un pacchetto di aggiornamento.")
    if not metadata.get("canInstall") or not metadata.get("updateAvailable"):
        raise HTTPException(status.HTTP_409_CONFLICT, "Il pacchetto non contiene una versione più recente di quella installata.")
    details: dict[str, Any] = {
        "source": payload.source,
        "targetVersion": metadata["latestVersion"],
        "sha256": str(metadata.get("sha256") or ""),
    }
    if payload.source == "github":
        details["assetUrl"] = str(metadata.get("assetUrl") or "")
        if not details["assetUrl"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "La release non contiene il pacchetto server installabile.")
    else:
        relative_path = str(metadata.get("filePath") or "")
        if not re.fullmatch(r"uploads/update-[0-9a-f-]{36}\.zip", relative_path):
            raise HTTPException(status.HTTP_409_CONFLICT, "Il file caricato non è più disponibile.")
        details["filePath"] = relative_path
    control_request = create_portal_request("update", admin, **details)
    audit(db, "admin.update_requested", request, actor=admin.id, target=admin.id, source=payload.source, version=metadata["latestVersion"])
    db.commit()
    return {"message": "Aggiornamento avviato. Backup, installazione e riavvio saranno automatici.", "requestId": control_request["requestId"], "version": metadata["latestVersion"]}


@app.post("/api/admin/server/restart", status_code=202)
def restart_portal(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if request.headers.get("x-confirm-portal-action") != "RESTART":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Conferma riavvio mancante.")
    control_request = create_portal_request("restart", admin)
    audit(db, "admin.portal_restart_requested", request, actor=admin.id, target=admin.id)
    db.commit()
    return {"message": "Riavvio del portale richiesto.", "requestId": control_request["requestId"]}


@app.post("/api/admin/server/stop", status_code=202)
def stop_portal(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if request.headers.get("x-confirm-portal-action") != "STOP":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Conferma spegnimento mancante.")
    control_request = create_portal_request("stop", admin)
    audit(db, "admin.portal_stop_requested", request, actor=admin.id, target=admin.id)
    db.commit()
    return {"message": "Spegnimento del solo portale richiesto. Il server e gli altri servizi restano accesi.", "requestId": control_request["requestId"]}


@app.put("/api/admin/settings")
def save_admin_settings(payload: CloudSettingsInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if payload.duckdns_enabled and (not payload.duckdns_domain or (not payload.duckdns_token and not get_setting(db, "duckdns_token"))):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Per attivare DuckDNS servono dominio e token.")
    if payload.smtp_enabled and (not payload.smtp_host or not payload.smtp_from_email):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Per attivare la posta servono server SMTP e mittente.")
    daily_challenge_config = normalized_challenge_composition(db)
    if payload.daily_challenge_config is not None:
        daily_challenge_config = normalize_daily_challenge_config(payload.daily_challenge_config, strict=True)
        validate_daily_challenge_capacity(daily_challenge_config, db)
    values = {
        "site_name": payload.site_name.strip(), "registration_enabled": payload.registration_enabled, "daily_challenge_enabled": payload.daily_challenge_enabled, "daily_challenge_required": payload.daily_challenge_required, "daily_challenge_config": daily_challenge_config, "public_url": payload.public_url,
        "session_days": payload.session_days, "reset_token_minutes": payload.reset_token_minutes, "privacy_notice": payload.privacy_notice.strip(),
        "privacy_controller_name": payload.privacy_controller_name.strip(), "privacy_controller_address": payload.privacy_controller_address.strip(),
        "privacy_contact_email": str(payload.privacy_contact_email or ""), "privacy_pec_email": str(payload.privacy_pec_email or ""),
        "privacy_dpo_contact": payload.privacy_dpo_contact.strip(), "privacy_hosting_location": payload.privacy_hosting_location.strip(),
        "privacy_email_provider": payload.privacy_email_provider.strip(), "privacy_transfer_note": payload.privacy_transfer_note.strip(),
        "privacy_policy_version": payload.privacy_policy_version.strip(), "privacy_effective_date": payload.privacy_effective_date,
        "privacy_audit_log_days": payload.privacy_audit_log_days, "privacy_backup_days": payload.privacy_backup_days,
        "duckdns_enabled": payload.duckdns_enabled, "duckdns_domain": payload.duckdns_domain, "duckdns_interval_minutes": payload.duckdns_interval_minutes,
        "smtp_enabled": payload.smtp_enabled, "smtp_host": payload.smtp_host.strip(), "smtp_port": payload.smtp_port,
        "smtp_username": payload.smtp_username.strip(), "smtp_from_email": str(payload.smtp_from_email or ""), "smtp_use_tls": payload.smtp_use_tls,
    }
    for key, value in values.items():
        set_setting(db, key, value)
    if payload.clear_duckdns_token:
        set_setting(db, "duckdns_token", "")
    elif payload.duckdns_token:
        set_setting(db, "duckdns_token", payload.duckdns_token.strip())
    if payload.clear_smtp_password:
        set_setting(db, "smtp_password", "")
    elif payload.smtp_password:
        set_setting(db, "smtp_password", payload.smtp_password)
    audit(db, "admin.settings_updated", request, actor=admin.id, target=admin.id)
    db.commit()
    if duckdns_wakeup:
        duckdns_wakeup.set()
    return admin_settings(admin, db)


@app.put("/api/admin/challenge-settings")
def save_daily_challenge_settings(payload: DailyChallengeSettingsInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    config = normalize_daily_challenge_config(payload.config, strict=True)
    validate_daily_challenge_capacity(config, db)
    set_setting(db, "daily_challenge_enabled", payload.enabled)
    set_setting(db, "daily_challenge_required", payload.required)
    set_setting(db, "daily_challenge_config", config)
    current_challenge = db.get(DailyChallenge, challenge_today())
    audit(
        db,
        "challenge.settings_updated",
        request,
        actor=admin.id,
        target=admin.id,
        currentChallengePreserved=bool(current_challenge),
        required=payload.required,
    )
    db.commit()
    return {
        "enabled": payload.enabled,
        "required": payload.required,
        "config": config,
        "currentChallengePreserved": bool(current_challenge),
        "message": "Configurazione salvata. La sfida eventualmente già creata oggi e la sua classifica non sono state modificate.",
    }


@app.post("/api/admin/settings/test-duckdns")
async def test_duckdns(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    result = await perform_duckdns_update(db)
    audit(db, "admin.duckdns_test", request, actor=admin.id, target=admin.id, success=True)
    db.commit()
    return result


@app.post("/api/admin/settings/test-email")
async def test_email(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, str]:
    if not admin.email:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Aggiungi prima un'email al tuo account.")
    try:
        await send_email(admin.email, "Test Quiz 400 VVF 2026", "La configurazione email del portale funziona correttamente.", db)
    except Exception as error:
        set_setting(db, "smtp_last_status", {"ok": False, "at": utcnow().isoformat(), "kind": "test", "message": str(error)[:300]})
        audit(db, "admin.smtp_test", request, actor=admin.id, target=admin.id, success=False)
        db.commit()
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Invio non riuscito: {error}") from error
    set_setting(db, "smtp_last_status", {"ok": True, "at": utcnow().isoformat(), "kind": "test", "message": "Email di prova consegnata al server SMTP."})
    audit(db, "admin.smtp_test", request, actor=admin.id, target=admin.id, success=True)
    db.commit()
    return {"message": f"Email di prova inviata a {admin.email}."}


@app.get("/api/admin/backup")
def download_backup(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> JSONResponse:
    users_rows = db.scalars(select(User)).all()
    challenge_rows = db.scalars(select(DailyChallenge).order_by(DailyChallenge.challenge_date)).all()
    attempt_rows = db.scalars(select(DailyChallengeAttempt).order_by(DailyChallengeAttempt.challenge_date, DailyChallengeAttempt.started_at)).all()
    report_rows = db.scalars(select(QuestionReport).order_by(QuestionReport.created_at)).all()
    disabled_rows = db.scalars(select(DisabledQuestion).order_by(DisabledQuestion.disabled_at)).all()
    rating_rows = db.scalars(select(QuestionRating).order_by(QuestionRating.created_at)).all()
    backup_users = []
    for row in users_rows:
        avatar = db.get(UserAvatar, row.id)
        backup_users.append({
            **serialize_user(row, include_state=True),
            "passwordHash": row.password_hash,
            "avatar": ({"data": avatar.data, "mime": avatar.mime, "updatedAt": aware_utc(avatar.updated_at).isoformat()} if avatar else None),
        })
    payload = {
        "app": "Quiz 400 VVF 2026 Cloud", "version": 5, "createdAt": utcnow().isoformat(),
        "users": backup_users,
        "settings": {key: (db.get(Setting, key).value if db.get(Setting, key) else DEFAULT_SETTINGS[key]) for key in DEFAULT_SETTINGS},
        "dailyChallenges": [{"date": row.challenge_date.isoformat(), "questionIds": row.question_ids, "composition": row.composition, "appVersion": row.app_version, "createdAt": aware_utc(row.created_at).isoformat()} for row in challenge_rows],
        "dailyChallengeAttempts": [{"id": row.id, "date": row.challenge_date.isoformat(), "userId": row.user_id, "answers": row.answers, "questionSeconds": row.question_seconds, "startedAt": aware_utc(row.started_at).isoformat(), "submittedAt": aware_utc(row.submitted_at).isoformat() if row.submitted_at else None, "correct": row.correct, "wrong": row.wrong, "blank": row.blank, "scoreX100": row.score_x100, "durationSeconds": row.duration_seconds} for row in attempt_rows],
        "questionReports": [{"id": row.id, "questionId": row.question_id, "userId": row.user_id, "reason": row.reason, "note": row.note, "status": row.status, "createdAt": aware_utc(row.created_at).isoformat(), "reviewedAt": aware_utc(row.reviewed_at).isoformat() if row.reviewed_at else None, "reviewedByUserId": row.reviewed_by_user_id, "reply": row.reply, "replyReadAt": aware_utc(row.reply_read_at).isoformat() if row.reply_read_at else None} for row in report_rows],
        "disabledQuestions": [{"questionId": row.question_id, "reason": row.reason, "disabledAt": aware_utc(row.disabled_at).isoformat(), "disabledByUserId": row.disabled_by_user_id} for row in disabled_rows],
        "questionRatings": [{"id": row.id, "questionId": row.question_id, "userId": row.user_id, "rating": row.rating, "createdAt": aware_utc(row.created_at).isoformat(), "updatedAt": aware_utc(row.updated_at).isoformat()} for row in rating_rows],
    }
    headers = {"Content-Disposition": f'attachment; filename="quiz-400-vvf-cloud-backup-{utcnow().date().isoformat()}.json"'}
    return JSONResponse(payload, headers=headers)


@app.post("/api/admin/restore", status_code=204)
async def restore_backup(request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> Response:
    if request.headers.get("x-confirm-restore") != "RESTORE":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Conferma ripristino mancante.")
    data = await request.json()
    if data.get("app") != "Quiz 400 VVF 2026 Cloud" or not isinstance(data.get("users"), list) or not isinstance(data.get("settings"), dict):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Backup non valido.")
    restore_admin_id = admin.id
    db.execute(QuestionRating.__table__.delete())
    db.execute(QuestionReport.__table__.delete())
    db.execute(DisabledQuestion.__table__.delete())
    db.execute(DailyChallengeAttempt.__table__.delete())
    db.execute(DailyChallenge.__table__.delete())
    db.execute(LoginSession.__table__.delete())
    db.execute(PasswordReset.__table__.delete())
    db.execute(UserAvatar.__table__.delete())
    db.execute(UserState.__table__.delete())
    db.execute(User.__table__.delete())
    db.flush()
    db.expunge_all()
    for item in data["users"]:
        user = User(
            id=item["id"],
            username=normalize_username(item["username"]),
            display_name=str(item["name"])[:100],
            email=normalize_email(item.get("email")),
            password_hash=item["passwordHash"],
            role=item.get("role", "user"),
            active=bool(item.get("active", True)),
            approved=bool(item.get("approved", True)),
            must_change_password=bool(item.get("mustChangePassword", False)),
            created_at=datetime.fromisoformat(item["createdAt"]),
            last_login_at=datetime.fromisoformat(item["lastLoginAt"]) if item.get("lastLoginAt") else None,
            privacy_policy_version=item.get("privacyPolicyVersion"),
            privacy_acknowledged_at=datetime.fromisoformat(item["privacyAcknowledgedAt"]) if item.get("privacyAcknowledgedAt") else None,
        )
        user.state = UserState(data=item.get("state") or empty_state(), revision=int(item.get("revision", 1) or 1))
        avatar = item.get("avatar")
        if isinstance(avatar, dict) and avatar.get("data") and avatar.get("mime"):
            try:
                avatar_content = base64.b64decode(str(avatar["data"]), validate=True)
            except (ValueError, TypeError):
                avatar_content = b""
            avatar_mime = str(avatar["mime"])
            if avatar_content and len(avatar_content) <= MAX_AVATAR_BYTES and image_signature_matches(avatar_mime, avatar_content):
                user.avatar = UserAvatar(
                    data=base64.b64encode(avatar_content).decode("ascii"),
                    mime=avatar_mime,
                    updated_at=datetime.fromisoformat(avatar["updatedAt"]) if avatar.get("updatedAt") else utcnow(),
                )
        db.add(user)
    db.flush()
    for item in data.get("dailyChallenges", []):
        if not isinstance(item, dict):
            continue
        db.add(DailyChallenge(challenge_date=date.fromisoformat(item["date"]), question_ids=list(item.get("questionIds") or []), composition=dict(item.get("composition") or {}), app_version=str(item.get("appVersion") or APP_VERSION), created_at=datetime.fromisoformat(item["createdAt"])))
    db.flush()
    for item in data.get("dailyChallengeAttempts", []):
        if not isinstance(item, dict):
            continue
        db.add(DailyChallengeAttempt(id=str(item["id"]), challenge_date=date.fromisoformat(item["date"]), user_id=str(item["userId"]), answers=list(item.get("answers") or [None] * 40), question_seconds=item.get("questionSeconds"), started_at=datetime.fromisoformat(item["startedAt"]), submitted_at=datetime.fromisoformat(item["submittedAt"]) if item.get("submittedAt") else None, correct=item.get("correct"), wrong=item.get("wrong"), blank=item.get("blank"), score_x100=item.get("scoreX100"), duration_seconds=item.get("durationSeconds")))
    for item in data.get("disabledQuestions", []):
        if not isinstance(item, dict) or not item.get("questionId"):
            continue
        db.add(DisabledQuestion(question_id=str(item["questionId"]), reason=str(item.get("reason") or ""), disabled_at=datetime.fromisoformat(item["disabledAt"]), disabled_by_user_id=item.get("disabledByUserId")))
    for item in data.get("questionReports", []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("questionId"):
            continue
        db.add(QuestionReport(id=str(item["id"]), question_id=str(item["questionId"]), user_id=item.get("userId"), reason=str(item.get("reason") or "other"), note=str(item.get("note") or ""), status=str(item.get("status") or "pending"), created_at=datetime.fromisoformat(item["createdAt"]), reviewed_at=datetime.fromisoformat(item["reviewedAt"]) if item.get("reviewedAt") else None, reviewed_by_user_id=item.get("reviewedByUserId"), reply=item.get("reply"), reply_read_at=datetime.fromisoformat(item["replyReadAt"]) if item.get("replyReadAt") else None))
    for item in data.get("questionRatings", []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("questionId") or not item.get("userId"):
            continue
        rating = int(item.get("rating") or 0)
        if rating not in (1, 2, 3):
            continue
        db.add(QuestionRating(id=str(item["id"]), question_id=str(item["questionId"]), user_id=str(item["userId"]), rating=rating, created_at=datetime.fromisoformat(item["createdAt"]), updated_at=datetime.fromisoformat(item["updatedAt"])))
    for key, value in data["settings"].items():
        if key in DEFAULT_SETTINGS:
            row = db.get(Setting, key)
            if row:
                row.value = value
            else:
                db.add(Setting(key=key, value=value))
    audit(db, "admin.backup_restored", request, actor=restore_admin_id, target=restore_admin_id)
    db.commit()
    return Response(status_code=204)


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: dict[str, Any]) -> Response:
        response = await super().get_response(path, scope)
        if path in {"index.html", "sw.js", "version.json"}:
            response.headers["Cache-Control"] = "no-cache"
        return response


app.mount("/", NoCacheStaticFiles(directory=ROOT, html=True), name="static")
