import os
from pathlib import Path
from unittest.mock import AsyncMock, patch


TEST_DB = Path(__file__).resolve().parents[2] / "tmp" / "cloud-test.sqlite3"
TEST_DB.parent.mkdir(parents=True, exist_ok=True)
TEST_DB.unlink(missing_ok=True)
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
            },
        )
        assert registration.status_code == 201
        assert public_client.post(
            "/api/auth/register",
            json={
                "username": "mario.rossi",
                "name": "Duplicato",
                "email": "altro@example.com",
                "password": "Altra-Sicura-2026!",
            },
        ).status_code == 409

        user_login = login(user_client, "mario.rossi", "Mario-Sicura-2026!")
        assert user_login.status_code == 200
        user_id = user_login.json()["user"]["id"]

        assert user_client.get("/api/admin/users").status_code == 403
        state = {
            "progress": {
                "vf20240001": {"attempts": 2, "correct": 2, "wrong": 0, "skipped": 0, "status": "known"},
                "vf20240002": {"attempts": 1, "correct": 0, "wrong": 1, "skipped": 0, "status": "unknown"},
            },
            "sessions": [
                {"type": "exam", "at": "2026-08-12T10:00:00+00:00", "correct": 30, "wrong": 5, "blank": 5, "score": 28.35}
            ],
        }
        save = user_client.put("/api/cloud/state", json={"state": state})
        assert save.status_code == 200
        assert save.json()["revision"] >= 2

        users = admin_client.get("/api/admin/users")
        assert users.status_code == 200
        mario = next(item for item in users.json()["users"] if item["id"] == user_id)
        assert mario["statistics"]["answered"] == 2
        assert mario["statistics"]["simulations"] == 1
        assert mario["statistics"]["averageScore"] == 28.35

        statistics = admin_client.get(f"/api/admin/users/{user_id}/statistics")
        assert statistics.status_code == 200
        assert statistics.json()["summary"]["known"] == 1
        assert statistics.json()["recentSessions"][0]["score"] == 28.35

        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"role": "admin"}).json()["user"]["role"] == "admin"
        assert admin_client.patch(f"/api/admin/users/{user_id}", json={"role": "user"}).json()["user"]["role"] == "user"

        settings_payload = {
            "site_name": "Quiz VVF Cloud Test",
            "registration_enabled": False,
            "public_url": "https://quiz-test.duckdns.org",
            "session_days": 14,
            "reset_token_minutes": 45,
            "privacy_notice": "Informativa di prova",
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
        assert "token-segreto-test" not in settings.text
        assert "smtp-secret-test" not in settings.text
        assert public_client.get("/api/internal/tls-allowed?domain=quiz-test.duckdns.org").status_code == 204
        assert public_client.get("/api/internal/tls-allowed?domain=evil.example.com").status_code == 403
        assert public_client.get("/api/runtime").json()["registrationEnabled"] is False
        assert public_client.get("/api/runtime").json()["emailResetEnabled"] is True

        recovery_token = "R" * 48
        with patch("cloud.app.secrets.token_urlsafe", return_value=recovery_token), patch(
            "cloud.app.send_email", new=AsyncMock()
        ) as mocked_email:
            forgotten = public_client.post("/api/auth/forgot-password", json={"account": "mario.rossi"})
            missing = public_client.post("/api/auth/forgot-password", json={"account": "inesistente"})
            assert forgotten.status_code == missing.status_code == 202
            assert forgotten.json()["message"] == missing.json()["message"]
            mocked_email.assert_awaited_once()
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
