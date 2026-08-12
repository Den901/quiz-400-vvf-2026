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
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Generator
from urllib.parse import urlparse

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{ROOT / 'cloud-data.sqlite3'}")
APP_SECRET = os.environ.get("APP_SECRET", "")
try:
    APP_VERSION = str(json.loads((ROOT / "version.json").read_text(encoding="utf-8"))["version"])
except (OSError, ValueError, KeyError, TypeError):
    APP_VERSION = "2.1.2"


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
MAX_LOGO_BYTES = 1024 * 1024
USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,39}$")
DUCKDNS_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.duckdns\.org)?$")

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
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    state: Mapped["UserState"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    sessions: Mapped[list["LoginSession"]] = relationship(cascade="all, delete-orphan")
    reset_tokens: Mapped[list["PasswordReset"]] = relationship(cascade="all, delete-orphan")


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


engine_options: dict[str, Any] = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


DEFAULT_SETTINGS: dict[str, Any] = {
    "site_name": "Quiz 400 VVF 2026",
    "registration_enabled": True,
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
    "privacy_notice": "I dati sono usati esclusivamente per gestire l'account e il percorso di studio.",
    "exam_config": {"examPlan": {"storia": 8, "logica": 11, "insiemi": 1, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4, "brani": 0}},
}
SECRET_SETTING_KEYS = {"duckdns_token", "smtp_password"}


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


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


def public_settings(db: Session) -> dict[str, Any]:
    logo_version = str(get_setting(db, "brand_logo_updated_at") or "default")
    logo_customized = bool(get_setting(db, "brand_logo_data"))
    return {
        "siteName": get_setting(db, "site_name"),
        "registrationEnabled": bool(get_setting(db, "registration_enabled")),
        "emailResetEnabled": bool(get_setting(db, "smtp_enabled") and get_setting(db, "smtp_host")),
        "privacyNotice": get_setting(db, "privacy_notice"),
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
    return {"progress": {}, "sessions": [], "categoryCursor": {}, "examCursor": {}, "examCount": 0, "quizGenerationCount": 0, "quizRotation": {}, "examPresets": [], "activeExamPresetId": None, "theme": "system"}


def serialize_user(user: User, include_state: bool = False) -> dict[str, Any]:
    payload = {
        "id": user.id,
        "username": user.username,
        "name": user.display_name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
        "mustChangePassword": user.must_change_password,
        "createdAt": user.created_at.isoformat(),
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
    }
    if include_state:
        payload["state"] = user.state.data if user.state else empty_state()
        payload["revision"] = user.state.revision if user.state else 0
    return payload


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
    return user if user and user.active else None


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = current_user_optional(request, db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Accesso richiesto.")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Permessi amministratore richiesti.")
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


class StateInput(BaseModel):
    state: dict[str, Any]
    config: dict[str, Any] | None = None


class AdminUserInput(RegistrationInput):
    role: str = "user"

    @field_validator("role")
    @classmethod
    def role_is_valid(cls, value: str) -> str:
        if value not in {"user", "admin"}:
            raise ValueError("Ruolo non valido.")
        return value


class AdminUserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    active: bool | None = None
    role: str | None = None


class AdminResetInput(BaseModel):
    password: str | None = Field(default=None, min_length=10, max_length=256)


class PortChangeInput(BaseModel):
    app_port: int = Field(ge=1024, le=65535)


class BrandLogoInput(BaseModel):
    data_url: str = Field(min_length=32, max_length=1_500_000)


class CloudSettingsInput(BaseModel):
    site_name: str = Field(min_length=3, max_length=100)
    registration_enabled: bool
    public_url: str = Field(default="", max_length=300)
    session_days: int = Field(ge=1, le=365)
    reset_token_minutes: int = Field(ge=10, le=1440)
    privacy_notice: str = Field(default="", max_length=2000)
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


def subject_session_statistics(state_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sessions = state_data.get("sessions", []) if isinstance(state_data, dict) else []
    sessions = sessions if isinstance(sessions, list) else []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        if not isinstance(session, dict) or session.get("type") not in {"study", "guided"}:
            continue
        per_category = session.get("perCategory")
        if isinstance(per_category, dict) and per_category:
            for category, payload in per_category.items():
                if not isinstance(payload, dict):
                    continue
                correct = numeric_value(payload.get("correct")) or 0
                wrong = numeric_value(payload.get("wrong")) or 0
                blank = numeric_value(payload.get("blank")) or 0
                grouped.setdefault(str(category), []).append(
                    {
                        **payload,
                        "score": round(correct - wrong * 0.33, 2),
                        "questionCount": numeric_value(payload.get("total")) or correct + wrong + blank,
                    }
                )
            continue
        category = session.get("category")
        if isinstance(category, str) and category:
            grouped.setdefault(category, []).append(session)
    return {category: session_group_statistics(rows) for category, rows in grouped.items()}


def state_statistics(state_data: dict[str, Any]) -> dict[str, Any]:
    progress = state_data.get("progress") if isinstance(state_data, dict) else {}
    sessions = state_data.get("sessions") if isinstance(state_data, dict) else []
    progress = progress if isinstance(progress, dict) else {}
    sessions = sessions if isinstance(sessions, list) else []
    values = [item for item in progress.values() if isinstance(item, dict)]
    valid_sessions = [item for item in sessions if isinstance(item, dict)]
    exams = [item for item in valid_sessions if item.get("type") == "exam"]
    forty_quizzes = [item for item in valid_sessions if item.get("type") in {"exam", "guided-exam"}]
    guided = [item for item in sessions if isinstance(item, dict) and item.get("type") in {"guided", "guided-exam"}]
    subject_quizzes = [item for item in sessions if isinstance(item, dict) and item.get("type") in {"study", "guided"}]
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
    }


question_categories: dict[str, str] = {}
question_category_totals: dict[str, int] = {}


def load_question_categories() -> None:
    global question_categories, question_category_totals
    try:
        rows = json.loads((ROOT / "quiz-dataset.json").read_text(encoding="utf-8"))
        question_categories = {str(row["id"]): str(row["category"]) for row in rows if isinstance(row, dict) and row.get("id") and row.get("category")}
        question_category_totals = {}
        for category in question_categories.values():
            question_category_totals[category] = question_category_totals.get(category, 0) + 1
    except (OSError, ValueError):
        question_categories = {}
        question_category_totals = {}


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
            user = User(username=admin_username, display_name=os.environ.get("ADMIN_NAME", "Amministratore")[:100], email=normalize_email(os.environ.get("ADMIN_EMAIL")), password_hash=password_hasher.hash(admin_password), role="admin", active=True)
            user.state = UserState(data=empty_state())
            db.add(user)
        db.execute(LoginSession.__table__.delete().where(LoginSession.expires_at <= utcnow()))
        db.execute(PasswordReset.__table__.delete().where(PasswordReset.expires_at <= utcnow()))
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
        if length > MAX_STATE_BYTES:
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
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
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
    return {"mode": "cloud", "version": APP_VERSION, **public_settings(db)}


def decode_logo_data_url(data_url: str) -> tuple[str, bytes, str]:
    match = re.fullmatch(r"data:(image/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=\r\n]+)", data_url.strip())
    if not match:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Usa un'immagine JPEG, PNG o WebP valida.")
    try:
        content = base64.b64decode(match.group(2), validate=True)
    except (ValueError, TypeError) as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Immagine non valida.") from error
    mime = match.group(1)
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    }
    if not content or len(content) > MAX_LOGO_BYTES or not signatures.get(mime, False):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Il logo deve essere JPEG, PNG o WebP e pesare al massimo 1 MB.")
    return mime, content, base64.b64encode(content).decode("ascii")


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
def register(payload: RegistrationInput, request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    enforce_rate_limit(request, "register", 8, 3600)
    if not get_setting(db, "registration_enabled"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Le registrazioni sono chiuse.")
    try:
        username = normalize_username(payload.username)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    email = normalize_email(str(payload.email) if payload.email else None)
    if db.scalar(select(User).where((User.username == username) | ((User.email == email) if email else False))):
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome utente o email già utilizzati.")
    user = User(username=username, display_name=payload.name.strip(), email=email, password_hash=password_hasher.hash(payload.password), role="user", active=True)
    user.state = UserState(data=empty_state())
    db.add(user)
    db.flush()
    audit(db, "user.registered", request, target=user.id)
    db.commit()
    return {"message": "Registrazione completata. Ora puoi accedere."}


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
        audit(db, "auth.login_failed", request, target=user.id if user else None, username=username)
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenziali non valide.")
    if password_hasher.check_needs_rehash(user.password_hash):
        user.password_hash = password_hasher.hash(payload.password)
    user.last_login_at = utcnow()
    create_session(db, user, request, response)
    audit(db, "auth.login", request, actor=user.id, target=user.id)
    db.commit()
    return {"user": serialize_user(user, include_state=True), "config": get_setting(db, "exam_config")}


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
    return {"user": serialize_user(user, include_state=True), "config": get_setting(db, "exam_config")}


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
        "admins": sum(1 for row in rows if row.role == "admin"),
        "simulations": sum(item["statistics"]["simulations"] for item in users_payload),
        "fortyQuizzes": forty_count,
        "subjectQuizzes": subject_count,
        "averageFortyScore": round(forty_score_total / forty_count, 2) if forty_count else None,
        "averageSubjectAccuracy": round(subject_accuracy_total / subject_count, 1) if subject_count else None,
    }
    return {"users": users_payload, "totals": totals}


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
    user = User(username=username, display_name=payload.name.strip(), email=email, password_hash=password_hasher.hash(payload.password), role=payload.role, active=True, must_change_password=True)
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
        if payload.role not in {"user", "admin"}:
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
    audit(db, "admin.user_deleted", request, actor=admin.id, target=target.id, username=target.username)
    db.delete(target)
    db.commit()
    return Response(status_code=204)


@app.get("/api/admin/settings")
def admin_settings(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "siteName": get_setting(db, "site_name"),
        "registrationEnabled": bool(get_setting(db, "registration_enabled")),
        "publicUrl": get_setting(db, "public_url"),
        "sessionDays": get_setting(db, "session_days"),
        "resetTokenMinutes": get_setting(db, "reset_token_minutes"),
        "privacyNotice": get_setting(db, "privacy_notice"),
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


@app.put("/api/admin/settings")
def save_admin_settings(payload: CloudSettingsInput, request: Request, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    if payload.duckdns_enabled and (not payload.duckdns_domain or (not payload.duckdns_token and not get_setting(db, "duckdns_token"))):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Per attivare DuckDNS servono dominio e token.")
    if payload.smtp_enabled and (not payload.smtp_host or not payload.smtp_from_email):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Per attivare la posta servono server SMTP e mittente.")
    values = {
        "site_name": payload.site_name.strip(), "registration_enabled": payload.registration_enabled, "public_url": payload.public_url,
        "session_days": payload.session_days, "reset_token_minutes": payload.reset_token_minutes, "privacy_notice": payload.privacy_notice.strip(),
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
    payload = {
        "app": "Quiz 400 VVF 2026 Cloud", "version": 1, "createdAt": utcnow().isoformat(),
        "users": [{**serialize_user(row, include_state=True), "passwordHash": row.password_hash} for row in users_rows],
        "settings": {key: (db.get(Setting, key).value if db.get(Setting, key) else DEFAULT_SETTINGS[key]) for key in DEFAULT_SETTINGS},
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
    db.execute(LoginSession.__table__.delete())
    db.execute(PasswordReset.__table__.delete())
    db.execute(UserState.__table__.delete())
    db.execute(User.__table__.delete())
    for item in data["users"]:
        user = User(id=item["id"], username=normalize_username(item["username"]), display_name=str(item["name"])[:100], email=normalize_email(item.get("email")), password_hash=item["passwordHash"], role=item.get("role", "user"), active=bool(item.get("active", True)), must_change_password=bool(item.get("mustChangePassword", False)), created_at=datetime.fromisoformat(item["createdAt"]))
        user.state = UserState(data=item.get("state") or empty_state(), revision=int(item.get("revision", 1) or 1))
        db.add(user)
    for key, value in data["settings"].items():
        if key in DEFAULT_SETTINGS:
            row = db.get(Setting, key)
            if row:
                row.value = value
            else:
                db.add(Setting(key=key, value=value))
    audit(db, "admin.backup_restored", request, actor=admin.id, target=admin.id)
    db.commit()
    return Response(status_code=204)


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: dict[str, Any]) -> Response:
        response = await super().get_response(path, scope)
        if path in {"index.html", "sw.js", "version.json"}:
            response.headers["Cache-Control"] = "no-cache"
        return response


app.mount("/", NoCacheStaticFiles(directory=ROOT, html=True), name="static")
