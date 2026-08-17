import hashlib
import io
import json
import os
import shutil
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


TEST_DB = Path(__file__).resolve().parents[2] / "tmp" / "cloud-test.sqlite3"
TEST_DB.parent.mkdir(parents=True, exist_ok=True)
TEST_DB.unlink(missing_ok=True)
PORT_CONTROL_DIR = TEST_DB.parent / "cloud-port-control-test"
PORT_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
for item in PORT_CONTROL_DIR.iterdir():
    shutil.rmtree(item) if item.is_dir() else item.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["APP_SECRET"] = "test-secret-for-cloud-integration"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_NAME"] = "Amministratore Test"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "Admin-Sicura-2026!"
os.environ["Q400_ENV"] = "test"
os.environ["PUBLIC_PROXY_MODE"] = "external"
os.environ["PUBLIC_APP_PORT"] = "18088"
os.environ["PUBLIC_APP_BIND_ADDRESS"] = "127.0.0.1"
os.environ["PORT_CONTROL_DIR"] = str(PORT_CONTROL_DIR)

from fastapi.testclient import TestClient

from cloud.app import app


def login(client: TestClient, username: str, password: str):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_complete_cloud_account_and_statistics_flow():
    with TestClient(app) as public_client:
        admin_client = TestClient(app)
        user_client = TestClient(app)
        runtime = public_client.get("/api/runtime")
        assert runtime.status_code == 200
        assert runtime.json()["mode"] == "cloud"
        assert runtime.json()["registrationEnabled"] is True
        assert runtime.json()["privacy"]["controllerName"] == "Titolare della demo"
        assert runtime.json()["privacy"]["complete"] is True
        policy_version = runtime.json()["privacy"]["policyVersion"]
        privacy = public_client.get("/api/privacy")
        assert privacy.status_code == 200
        assert privacy.json()["contactEmail"] == "privacy@example.com"
        assert privacy.json()["pecEmail"] == "privacy@pec.example.com"

        admin_login = login(admin_client, "admin", "Admin-Sicura-2026!")
        assert admin_login.status_code == 200
        assert admin_login.json()["user"]["role"] == "admin"
        assert "passwordHash" not in admin_login.text

        registration = public_client.post(
            "/api/auth/register",
            json={
                "username": "mario.rossi",
                "name": "Mario Rossi",
                "email": "mario@example.com",
                "password": "Mario-Sicura-2026!",
                "privacy_acknowledged": True,
                "privacy_policy_version": policy_version,
            },
        )
        assert registration.status_code == 201
        assert public_client.post(
            "/api/auth/register",
            json={
                "username": "senza.email",
                "name": "Senza Email",
                "password": "Sicura-Senza-Email-2026!",
            },
        ).status_code == 422
        assert public_client.post(
            "/api/auth/register",
            json={
                "username": "mario.rossi",
                "name": "Duplicato",
                "email": "altro@example.com",
                "password": "Altra-Sicura-2026!",
                "privacy_acknowledged": True,
                "privacy_policy_version": policy_version,
            },
        ).status_code == 409

        stale_policy = public_client.post(
            "/api/auth/register",
            json={
                "username": "policy.stale",
                "name": "Policy Stale",
                "email": "stale@example.com",
                "password": "Policy-Stale-2026!",
                "privacy_acknowledged": True,
                "privacy_policy_version": "old-version",
            },
        )
        assert stale_policy.status_code == 409

        user_login = login(user_client, "mario.rossi", "Mario-Sicura-2026!")
        assert user_login.status_code == 200
        user_id = user_login.json()["user"]["id"]
        assert user_login.json()["user"]["privacyPolicyVersion"] == policy_version
        assert user_login.json()["user"]["privacyAcknowledgedAt"]

        assert user_client.get("/api/admin/users").status_code == 403
        state = {
            "progress": {
                "25290564": {"attempts": 2, "correct": 2, "wrong": 0, "skipped": 0, "status": "known"},
                "25290565": {"attempts": 1, "correct": 0, "wrong": 1, "skipped": 0, "status": "review"},
            },
            "sessions": [
                {"type": "study", "at": "2026-08-12T08:00:00+00:00", "correct": 7, "wrong": 3, "blank": 0, "score": 6.01, "accuracy": 70, "questionCount": 10, "category": "chimica", "perCategory": {"chimica": {"correct": 7, "wrong": 3, "blank": 0, "total": 10, "accuracy": 70}}},
                {"type": "guided", "at": "2026-08-12T09:00:00+00:00", "correct": 4, "wrong": 1, "blank": 0, "score": 3.67, "accuracy": 80, "questionCount": 5, "category": "fisica", "perCategory": {"fisica": {"correct": 4, "wrong": 1, "blank": 0, "total": 5, "accuracy": 80}}},
                {"type": "exam", "at": "2026-08-12T10:00:00+00:00", "correct": 30, "wrong": 5, "blank": 5, "score": 28.35, "accuracy": 86},
                {"type": "guided-exam", "at": "2026-08-12T11:00:00+00:00", "correct": 32, "wrong": 4, "blank": 4, "score": 30.68, "accuracy": 89},
            ],
            "quizRotation": {"exam:chimica": {"cursor": 12, "cycle": 0, "size": 1677}},
            "examPresets": [{"id": "preset-mario", "name": "Prova personale", "plan": {"storia": 8, "logica": 11, "insiemi": 1, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4, "brani": 0}}],
            "activeExamPresetId": "preset-mario",
            "theme": "dark",
            "deepLearning": {
                "enabled": True,
                "tracks": {
                    "exam:chimica": {"cycle": 1, "size": 1677, "mastered": ["25290564"]}
                },
            },
            "deepLearningIntroSeen": True,
        }
        save = user_client.put("/api/cloud/state", json={"state": state})
        assert save.status_code == 200
        assert save.json()["revision"] >= 2

        users = admin_client.get("/api/admin/users")
        assert users.status_code == 200
        mario = next(item for item in users.json()["users"] if item["id"] == user_id)
        assert mario["statistics"]["answered"] == 2
        assert mario["statistics"]["simulations"] == 1
        assert mario["statistics"]["guidedQuizzes"] == 2
        assert mario["statistics"]["fortyQuizzes"] == 2
        assert mario["statistics"]["averageFortyScore"] == 29.52
        assert mario["statistics"]["averageFortyAccuracy"] == 87.5
        assert mario["statistics"]["subjectQuizzes"] == 2
        assert mario["statistics"]["averageSubjectScore"] == 4.84
        assert mario["statistics"]["averageSubjectAccuracy"] == 75.0
        assert mario["statistics"]["averageScore"] == 28.35
        assert users.json()["totals"]["fortyQuizzes"] == 2
        assert users.json()["totals"]["averageFortyScore"] == 29.52
        assert users.json()["totals"]["subjectQuizzes"] == 2
        assert users.json()["totals"]["averageSubjectAccuracy"] == 75.0

        assert user_client.get("/api/auth/me").json()["user"]["state"]["examPresets"][0]["id"] == "preset-mario"
        assert admin_client.get("/api/auth/me").json()["user"]["state"]["examPresets"] == []
        assert user_client.get("/api/auth/me").json()["user"]["state"]["theme"] == "dark"
        assert admin_client.get("/api/auth/me").json()["user"]["state"]["theme"] == "system"
        assert user_client.get("/api/auth/me").json()["user"]["state"]["deepLearning"]["enabled"] is True
        assert admin_client.get("/api/auth/me").json()["user"]["state"]["deepLearning"]["enabled"] is False
        assert user_client.get("/api/auth/me").json()["user"]["state"]["deepLearningIntroSeen"] is True
        assert admin_client.get("/api/auth/me").json()["user"]["state"]["deepLearningIntroSeen"] is False
        personal_export = user_client.get("/api/account/data-export")
        assert personal_export.status_code == 200
        assert personal_export.json()["profile"]["id"] == user_id
        assert "passwordHash" not in personal_export.text
        assert "token" not in personal_export.text.lower()

        statistics = admin_client.get(f"/api/admin/users/{user_id}/statistics")
        assert statistics.status_code == 200
        assert statistics.json()["summary"]["known"] == 1
        assert statistics.json()["summary"]["review"] == 1
        assert statistics.json()["categories"]["chimica"]["total"] == 1677
        assert statistics.json()["categories"]["chimica"]["toDo"] == 1675
        assert statistics.json()["categories"]["chimica"]["accuracy"] == 67
        assert statistics.json()["categories"]["chimica"]["quizCount"] == 1
        assert statistics.json()["categories"]["chimica"]["averageQuizScore"] == 6.01
        assert statistics.json()["categories"]["chimica"]["averageQuizAccuracy"] == 70.0
        assert statistics.json()["categories"]["chimica"]["averageQuizQuestions"] == 10.0
        assert statistics.json()["recentSessions"][0]["type"] == "guided-exam"

        logo_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        logo = admin_client.post("/api/admin/branding/logo", json={"data_url": logo_data})
        assert logo.status_code == 200
        assert logo.json()["logoCustomized"] is True
        assert public_client.get("/api/branding/logo").headers["content-type"].startswith("image/png")
        manifest = public_client.get("/manifest.webmanifest")
        assert manifest.status_code == 200
        assert manifest.json()["icons"][0]["src"].startswith("./api/branding/logo?v=")
        assert manifest.json()["icons"][0]["type"] == "image/png"
        assert manifest.json()["icons"][0]["sizes"] == "any"
        assert admin_client.get("/api/admin/settings").json()["logoCustomized"] is True
        reset_logo = admin_client.delete("/api/admin/branding/logo")
        assert reset_logo.status_code == 200
        assert reset_logo.json()["logoCustomized"] is False
        assert public_client.get("/api/branding/logo").headers["content-type"].startswith("image/jpeg")

        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"role": "admin"}).json()["user"]["role"] == "admin"
        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"role": "user"}).json()["user"]["role"] == "user"

        settings_payload = {
            "site_name": "Quiz VVF Cloud Test",
            "registration_enabled": False,
            "public_url": "https://quiz-test.duckdns.org",
            "session_days": 14,
            "reset_token_minutes": 45,
            "privacy_notice": "Informativa di prova",
            "privacy_controller_name": "Titolare del test",
            "privacy_controller_address": "",
            "privacy_contact_email": "privacy@example.com",
            "privacy_pec_email": "privacy@pec.example.com",
            "privacy_dpo_contact": "",
            "privacy_hosting_location": "Italia (server test)",
            "privacy_email_provider": "Provider SMTP di test",
            "privacy_transfer_note": "Nessun trasferimento nel test.",
            "privacy_policy_version": "2026-08-test",
            "privacy_effective_date": "2026-08-14",
            "privacy_audit_log_days": 120,
            "privacy_backup_days": 30,
            "duckdns_enabled": True,
            "duckdns_domain": "quiz-test.duckdns.org",
            "duckdns_token": "token-segreto-test",
            "duckdns_interval_minutes": 10,
            "smtp_enabled": True,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "mailer@example.com",
            "smtp_password": "smtp-secret-test",
            "smtp_from_email": "mailer@example.com",
            "smtp_use_tls": True,
        }
        settings = admin_client.put("/api/admin/settings", json=settings_payload)
        assert settings.status_code == 200
        assert settings.json()["duckdnsTokenConfigured"] is True
        assert settings.json()["deploymentProxyMode"] == "external"
        assert settings.json()["deploymentAppPort"] == 18088
        assert settings.json()["deploymentBindAddress"] == "127.0.0.1"
        assert settings.json()["portControl"]["available"] is True
        assert "token-segreto-test" not in settings.text
        assert "smtp-secret-test" not in settings.text
        assert public_client.get("/api/internal/tls-allowed?domain=quiz-test.duckdns.org").status_code == 204
        assert public_client.get("/api/internal/tls-allowed?domain=evil.example.com").status_code == 403
        assert public_client.get("/api/runtime").json()["registrationEnabled"] is False
        assert public_client.get("/api/runtime").json()["emailResetEnabled"] is True
        assert public_client.get("/api/runtime").json()["privacy"]["policyVersion"] == "2026-08-test"
        assert admin_client.get("/api/admin/settings").json()["privacyComplete"] is True

        assert user_client.post("/api/admin/network/apply", json={"app_port": 18089}).status_code == 403
        port_change = admin_client.post("/api/admin/network/apply", json={"app_port": 18089})
        assert port_change.status_code == 202
        port_request = __import__("json").loads((PORT_CONTROL_DIR / "request.json").read_text(encoding="utf-8"))
        assert port_request["currentPort"] == 18088
        assert port_request["appPort"] == 18089
        assert port_request["domain"] == "quiz-test.duckdns.org"

        update_status = admin_client.get("/api/admin/update/status")
        assert update_status.status_code == 200
        assert update_status.json()["currentVersion"] == "2.5.1"
        assert update_status.json()["database"] == "PostgreSQL"
        assert update_status.json()["control"]["available"] is True
        assert user_client.get("/api/admin/update/status").status_code == 403

        github_response = MagicMock()
        github_response.raise_for_status.return_value = None
        github_response.json.return_value = {
            "tag_name": "v9.9.9",
            "body": "- Changelog di prova",
            "html_url": "https://github.com/Den901/quiz-400-vvf-2026/releases/tag/v9.9.9",
            "published_at": "2026-08-14T10:00:00Z",
            "assets": [{"name": "Quiz-400-VVF-2026-Server.zip", "size": 1234, "browser_download_url": "https://github.com/Den901/quiz-400-vvf-2026/releases/download/v9.9.9/Quiz-400-VVF-2026-Server.zip"}],
        }
        github_client = MagicMock()
        github_client.get = AsyncMock(return_value=github_response)
        github_context = MagicMock()
        github_context.__aenter__ = AsyncMock(return_value=github_client)
        github_context.__aexit__ = AsyncMock(return_value=None)
        with patch("cloud.app.httpx.AsyncClient", return_value=github_context):
            checked = admin_client.post("/api/admin/update/check")
        assert checked.status_code == 200
        assert checked.json()["latestVersion"] == "9.9.9"
        assert checked.json()["updateAvailable"] is True
        assert checked.json()["canInstall"] is True
        assert "assetUrl" not in checked.json()

        install_github = admin_client.post("/api/admin/update/install", json={"source": "github"})
        assert install_github.status_code == 202
        server_request = json.loads((PORT_CONTROL_DIR / "server-request.json").read_text(encoding="utf-8"))
        assert server_request["action"] == "update"
        assert server_request["source"] == "github"
        assert server_request["targetVersion"] == "9.9.9"
        (PORT_CONTROL_DIR / "server-request.json").unlink()

        app_content = b"console.log('test update');\n"
        version_content = json.dumps({"name": "Quiz 400 VVF 2026", "version": "9.9.8"}).encode()
        manifest = {
            "app": "Quiz 400 VVF 2026 Server",
            "version": "9.9.8",
            "platform": "Linux e Windows",
            "changelog": ["Pacchetto manuale di prova"],
            "files": [
                {"path": "app.js", "sha256": hashlib.sha256(app_content).hexdigest(), "size": len(app_content)},
                {"path": "version.json", "sha256": hashlib.sha256(version_content).hexdigest(), "size": len(version_content)},
            ],
            "removedFiles": [],
        }
        package = io.BytesIO()
        with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("app.js", app_content)
            archive.writestr("version.json", version_content)
            archive.writestr("release-manifest.json", json.dumps(manifest))
        uploaded = admin_client.post(
            "/api/admin/update/upload",
            files={"file": ("Quiz-400-VVF-2026-Server.zip", package.getvalue(), "application/zip")},
        )
        assert uploaded.status_code == 201
        assert uploaded.json()["latestVersion"] == "9.9.8"
        assert uploaded.json()["canInstall"] is True
        assert "filePath" not in uploaded.json()
        install_upload = admin_client.post("/api/admin/update/install", json={"source": "upload"})
        assert install_upload.status_code == 202
        upload_request = json.loads((PORT_CONTROL_DIR / "server-request.json").read_text(encoding="utf-8"))
        assert upload_request["source"] == "upload"
        assert upload_request["filePath"].startswith("uploads/update-")
        (PORT_CONTROL_DIR / "server-request.json").unlink()

        assert admin_client.post("/api/admin/server/restart").status_code == 400
        restart = admin_client.post("/api/admin/server/restart", headers={"X-Confirm-Portal-Action": "RESTART"})
        assert restart.status_code == 202
        assert json.loads((PORT_CONTROL_DIR / "server-request.json").read_text(encoding="utf-8"))["action"] == "restart"
        (PORT_CONTROL_DIR / "server-request.json").unlink()
        assert admin_client.post("/api/admin/server/stop").status_code == 400
        stop = admin_client.post("/api/admin/server/stop", headers={"X-Confirm-Portal-Action": "STOP"})
        assert stop.status_code == 202
        assert json.loads((PORT_CONTROL_DIR / "server-request.json").read_text(encoding="utf-8"))["action"] == "stop"
        (PORT_CONTROL_DIR / "server-request.json").unlink()

        recovery_token = "R" * 48
        with patch("cloud.app.secrets.token_urlsafe", return_value=recovery_token), patch(
            "cloud.app.send_email", new=AsyncMock()
        ) as mocked_email:
            forgotten = public_client.post("/api/auth/forgot-password", json={"account": "mario.rossi"})
            missing = public_client.post("/api/auth/forgot-password", json={"account": "inesistente"})
            assert forgotten.status_code == missing.status_code == 202
            assert forgotten.json()["message"] == missing.json()["message"]
            mocked_email.assert_awaited_once()
        assert admin_client.get("/api/admin/settings").json()["smtpLastStatus"]["ok"] is True
        recovered = public_client.post(
            "/api/auth/reset-password",
            json={"token": recovery_token, "password": "Mario-Recuperata-2026!"},
        )
        assert recovered.status_code == 204
        assert login(TestClient(app), "mario.rossi", "Mario-Recuperata-2026!").status_code == 200

        reset = admin_client.post(f"/api/admin/users/{user_id}/reset-password", json={})
        assert reset.status_code == 200
        temporary_password = reset.json()["temporaryPassword"]
        assert len(temporary_password) == 16
        assert user_client.get("/api/auth/me").status_code == 401

        new_user_client = TestClient(app)
        temporary_login = login(new_user_client, "mario.rossi", temporary_password)
        assert temporary_login.status_code == 200
        assert temporary_login.json()["user"]["mustChangePassword"] is True
        changed = new_user_client.post(
            "/api/auth/change-password",
            json={"current_password": temporary_password, "new_password": "Mario-Nuova-2026!"},
        )
        assert changed.status_code == 204

        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"active": False}).status_code == 200
        assert login(TestClient(app), "mario.rossi", "Mario-Nuova-2026!").status_code == 401
        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"active": True}).status_code == 200

        backup = admin_client.get("/api/admin/backup")
        assert backup.status_code == 200
        assert backup.json()["app"] == "Quiz 400 VVF 2026 Cloud"
        assert len(backup.json()["users"]) == 2

        csrf = admin_client.put(
            "/api/admin/settings",
            json=settings_payload,
            headers={"Origin": "https://evil.example.com"},
        )
        assert csrf.status_code == 403

        assert admin_client.patch(
            f"/api/admin/users/{admin_login.json()['user']['id']}", json={"active": False}
        ).status_code == 409
        assert admin_client.delete(f"/api/admin/users/{user_id}").status_code == 204
        assert admin_client.get(f"/api/admin/users/{user_id}/statistics").status_code == 404
