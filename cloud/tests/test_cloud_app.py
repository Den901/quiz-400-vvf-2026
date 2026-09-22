import hashlib
import io
import json
import os
import shutil
import zipfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


TEST_DB = Path(__file__).resolve().parents[2] / "tmp" / "cloud-test-ratings.sqlite3"
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

from cloud.app import DEFAULT_AVATAR_BYTES, SessionLocal, app, available_forty_question_bank, available_question_bank, build_daily_challenge, challenge_today, rotating_daily_questions, set_setting

def test_gear_question_one_off_keeps_daily_composition():
    from datetime import date
    with TestClient(app):
        with SessionLocal() as db:
            challenge = build_daily_challenge(date(2026, 9, 14), db)
            assert len(challenge.question_ids) == len(set(challenge.question_ids)) == 40
            assert sum(q.startswith('gear-logic-') for q in challenge.question_ids) == 1
            assert 'gear-logic-q41' in challenge.question_ids
            assert challenge.composition['logicPlan']['ingranaggi'] == 1
            assert challenge.composition['logicPlan']['flow-chart'] == 1
            assert sum(q.startswith('flow-logic-') for q in challenge.question_ids) == 1
            assert sum(challenge.composition['logicPlan'].values()) == 12
            assert challenge.composition['examPlan'] == {'storia': 8, 'logica': 12, 'fisica': 6, 'chimica': 6, 'informatica': 4, 'inglese': 4}


def login(client: TestClient, username: str, password: str):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_every_daily_challenge_has_exactly_one_office_question_from_september_15():
    from datetime import date
    from cloud.app import questions_by_id
    with TestClient(app):
        with SessionLocal() as db:
            for day in [date(2026,9,15),date(2026,9,16),date(2027,1,1)]:
                challenge=build_daily_challenge(day,db)
                selected=[questions_by_id[q] for q in challenge.question_ids]
                assert len(selected)==40
                assert sum(q['category']=='informatica' for q in selected)==4
                assert sum(q['id'].startswith('office-mininterno-') for q in selected)==1
                assert sum(q['category']=='informatica' and bool(q.get('image')) for q in selected)==1


def test_daily_challenge_rotation_prefers_unseen_then_oldest_questions():
    source = [{"id": question_id} for question_id in ("a", "b", "c", "d")]
    today = challenge_today()
    usage = {
        "a": (1, today - timedelta(days=3)),
        "b": (1, today - timedelta(days=1)),
        "d": (2, today - timedelta(days=4)),
    }

    selected = rotating_daily_questions(source, 2, "rotation-test", usage)
    selected_ids = [row["id"] for row in selected]

    assert selected_ids[0] == "c"
    assert selected_ids[1] == "a"


def test_daily_challenge_excludes_misclassified_summaries():
    from cloud.app import challenge_logic_topic
    dataset = json.loads((Path(__file__).resolve().parents[2] / "quiz-dataset.json").read_text(encoding="utf-8"))
    summaries = [q for q in dataset if q.get("category") == "logica" and "sintetizza il testo" in q.get("text", "").lower()]
    assert len(summaries) == 60
    assert all(challenge_logic_topic(q) == "brani" for q in summaries)
    assert challenge_logic_topic({"category": "logica", "logicTopic": "deduzioni", "text": "Se tutti i gatti sono mammiferi, quale conclusione è corretta?"}) == "deduzioni"


def test_complete_cloud_account_and_statistics_flow():
    with TestClient(app) as public_client:
        admin_client = TestClient(app)
        user_client = TestClient(app)
        runtime = public_client.get("/api/runtime")
        assert runtime.status_code == 200
        assert runtime.json()["mode"] == "cloud"
        assert runtime.json()["version"] == "3.37.0"
        assert runtime.json()["releaseNotes"]["version"] == "3.37.0"
        assert runtime.json()["releaseNotes"]["showToUsers"] is False
        assert runtime.json()["releaseNotes"]["actionHash"] == "#moderation"
        assert runtime.json()["registrationEnabled"] is True
        assert runtime.json()["additionalQuestionBanks"] == {"nissolinoHistory": True, "modernHistory": True}
        assert runtime.json()["privacy"]["controllerName"] == "Titolare della demo"
        assert runtime.json()["privacy"]["complete"] is True
        app_shell = public_client.get("/")
        assert app_shell.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors 'none'" in app_shell.headers["content-security-policy"]
        assert 'class="nav-book-icon"' in app_shell.text
        assert "📖" not in app_shell.text
        assert ">Materie</a>" in app_shell.text
        assert 'data-route="data"' not in app_shell.text
        study_lesson = public_client.get("/study-content/chimica-generale.json")
        assert study_lesson.status_code == 200
        assert study_lesson.json()["id"] == "chimica-generale"
        assert len(study_lesson.json()["sections"]) > 10
        policy_version = runtime.json()["privacy"]["policyVersion"]
        privacy = public_client.get("/api/privacy")
        assert privacy.status_code == 200
        assert privacy.json()["contactEmail"] == "privacy@example.com"
        assert privacy.json()["pecEmail"] == "privacy@pec.example.com"

        admin_login = login(admin_client, "admin", "Admin-Sicura-2026!")
        assert admin_login.status_code == 200
        assert admin_login.json()["user"]["role"] == "admin"
        assert "passwordHash" not in admin_login.text

        moderator_created = admin_client.post(
            "/api/admin/users",
            json={"username": "moderatore", "name": "Moderatore Test", "email": "moderatore@example.com", "password": "Moderatore-2026!", "role": "moderator"},
        )
        assert moderator_created.status_code == 201
        moderator_client = TestClient(app)
        moderator_login = login(moderator_client, "moderatore", "Moderatore-2026!")
        assert moderator_login.status_code == 200
        assert moderator_login.json()["user"]["role"] == "moderator"
        assert moderator_login.json()["user"]["activeChallengeMonitorEnabled"] is True
        with SessionLocal() as db:
            set_setting(db, "daily_challenge_required", True)
            db.commit()
        assert moderator_client.get("/api/auth/me").json()["challengeGate"]["required"] is True
        moderator_id = moderator_login.json()["user"]["id"]
        exemption = admin_client.patch(f"/api/admin/users/{moderator_id}", json={"daily_challenge_required": False})
        assert exemption.status_code == 200
        assert exemption.json()["user"]["dailyChallengeRequired"] is False
        assert moderator_client.get("/api/auth/me").json()["challengeGate"]["required"] is False
        assert moderator_client.patch(f"/api/admin/users/{moderator_id}", json={"daily_challenge_required": True}).status_code == 403
        assert admin_client.patch(f"/api/admin/users/{moderator_id}", json={"daily_challenge_required": True}).status_code == 200
        with SessionLocal() as db:
            set_setting(db, "daily_challenge_required", False)
            db.commit()
        assert moderator_client.get("/api/admin/dashboard").status_code == 200
        assert moderator_client.get("/api/admin/users").status_code == 403
        assert moderator_client.get("/api/moderation/active-challenges").status_code == 200
        monitor_off = admin_client.patch(f"/api/admin/users/{moderator_id}", json={"active_challenge_monitor_enabled": False})
        assert monitor_off.status_code == 200
        assert monitor_off.json()["user"]["activeChallengeMonitorEnabled"] is False
        assert moderator_client.get("/api/moderation/active-challenges").status_code == 403
        assert admin_client.patch(f"/api/admin/users/{moderator_id}", json={"active_challenge_monitor_enabled": True}).status_code == 200
        assert moderator_client.put("/api/admin/dashboard/settings", json={"theoretical_cutoff": 20}).status_code == 403
        assert moderator_client.delete("/api/admin/dashboard/challenges/inesistente").status_code == 403

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
        assert "attesa di approvazione" in registration.json()["message"]
        with SessionLocal() as db:
            from cloud.app import User
            from sqlalchemy import select
            registered = db.scalar(select(User).where(User.username == "mario.rossi"))
            assert registered.daily_challenge_required is True
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

        pending_login = login(user_client, "mario.rossi", "Mario-Sicura-2026!")
        assert pending_login.status_code == 403
        pending_users = admin_client.get("/api/admin/users").json()
        pending_mario = next(item for item in pending_users["users"] if item["username"] == "mario.rossi")
        assert pending_mario["approved"] is False
        assert pending_users["totals"]["pendingApproval"] == 1
        pending_count = admin_client.get("/api/admin/users/pending-count")
        assert pending_count.status_code == 200
        assert pending_count.json() == {"pendingCount": 1}
        moderator_pending = moderator_client.get("/api/moderation/pending-users")
        assert moderator_pending.status_code == 200
        assert moderator_pending.json()["users"][0]["username"] == "mario.rossi"
        assert user_client.get("/api/admin/users/pending-count").status_code == 401
        user_id = pending_mario["id"]
        approval = moderator_client.post(f"/api/moderation/pending-users/{user_id}/approve")
        assert approval.status_code == 200
        assert approval.json()["approvedBy"] == "Moderatore Test"
        assert moderator_client.get("/api/moderation/pending-users").json()["pendingCount"] == 0
        assert approval.json()["user"]["approved"] is True
        assert admin_client.get("/api/admin/users/pending-count").json() == {"pendingCount": 0}

        user_login = login(user_client, "mario.rossi", "Mario-Sicura-2026!")
        assert user_login.status_code == 200
        assert user_login.json()["user"]["id"] == user_id
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
        dashboard = admin_client.get("/api/admin/dashboard")
        assert dashboard.status_code == 200
        assert dashboard.json()["summary"]["eligibleCandidates"] == 3
        assert dashboard.json()["summary"]["participants"] == 0
        assert dashboard.json()["summary"]["attempts"] == 0
        assert dashboard.json()["summary"]["averageAttemptScore"] is None
        assert dashboard.json()["summary"]["theoreticalCutoff"] == 14.71
        assert dashboard.json()["summary"]["candidatesAboveCutoff"] == 0
        assert dashboard.json()["summary"]["candidatesBelowCutoff"] == 0
        assert sum(item["count"] for item in dashboard.json()["bands"]) == 0
        assert dashboard.json()["bands"][0]["label"] == "Molto preparati · 32–40"
        assert len(dashboard.json()["types"]) == 1
        assert dashboard.json()["types"][0]["type"] == "daily-challenge"
        assert dashboard.json()["types"][0]["count"] == 0
        assert len(dashboard.json()["trend"]) == 14
        assert user_client.get("/api/admin/dashboard").status_code == 403
        cutoff_update = admin_client.put("/api/admin/dashboard/settings", json={"theoretical_cutoff": 16.25})
        assert cutoff_update.status_code == 200
        assert cutoff_update.json()["theoreticalCutoff"] == 16.25
        assert admin_client.get("/api/admin/settings").json()["theoreticalCutoff"] == 16.25
        updated_dashboard = admin_client.get("/api/admin/dashboard").json()
        assert updated_dashboard["summary"]["theoreticalCutoff"] == 16.25
        assert user_client.put("/api/admin/dashboard/settings", json={"theoretical_cutoff": 14.71}).status_code == 403
        assert admin_client.put("/api/admin/dashboard/settings", json={"theoretical_cutoff": 40.01}).status_code == 422
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

        assert public_client.get("/api/challenges/today").status_code == 401
        user_challenge = user_client.get("/api/challenges/today")
        admin_challenge = admin_client.get("/api/challenges/today")
        assert user_challenge.status_code == admin_challenge.status_code == 200
        assert user_challenge.json()["status"] == "not_started"
        assert user_challenge.json()["questionCount"] == 40
        assert sum(user_challenge.json()["composition"]["examPlan"].values()) == 40
        assert user_challenge.json()["composition"]["logicPlan"]["brani"] == 0
        original_challenge_composition = user_challenge.json()["composition"]

        required_setting = admin_client.put(
            "/api/admin/challenge-settings",
            json={"enabled": True, "required": True, "config": original_challenge_composition},
        )
        assert required_setting.status_code == 200
        assert required_setting.json()["required"] is True
        assert user_client.get("/api/auth/me").json()["challengeGate"] == {
            "required": True,
            "completed": False,
            "date": challenge_today().isoformat(),
            "status": "not_started",
            "forcedRedo": False,
            "forcedReason": None,
            "forcedBy": None,
            "forcedAt": None,
        }
        assert admin_client.get("/api/auth/me").json()["challengeGate"]["required"] is False

        user_start = user_client.post("/api/challenges/today/start", json={})
        admin_start = admin_client.post("/api/challenges/today/start", json={})
        assert user_start.status_code == admin_start.status_code == 200
        assert user_start.json()["status"] == "active"
        assert len(user_start.json()["questions"]) == 40
        assert [item["id"] for item in user_start.json()["questions"]] == [item["id"] for item in admin_start.json()["questions"]]
        original_challenge_ids = [item["id"] for item in user_start.json()["questions"]]
        assert all(item["category"] != "brani" for item in user_start.json()["questions"])
        assert all("correct" not in item and "explanation" not in item for item in user_start.json()["questions"])
        active_monitor = moderator_client.get("/api/moderation/active-challenges")
        assert active_monitor.status_code == 200
        assert active_monitor.json()["count"] == 2
        assert {item["username"] for item in active_monitor.json()["attempts"]} == {"admin", "mario.rossi"}
        assert all(0 < item["remainingSeconds"] <= 2400 for item in active_monitor.json()["attempts"])

        challenge_date = user_start.json()["date"]
        answers = [0] * 40
        question_seconds = list(range(1, 41))
        draft = user_client.put(f"/api/challenges/{challenge_date}/answers", json={"answers": answers, "questionSeconds": question_seconds})
        assert draft.status_code == 200
        assert draft.json()["answered"] == 40
        submitted = user_client.post(f"/api/challenges/{challenge_date}/submit", json={"answers": answers, "questionSeconds": question_seconds})
        assert submitted.status_code == 200
        assert submitted.json()["status"] == "completed"
        assert user_client.get("/api/auth/me").json()["challengeGate"]["completed"] is True
        assert submitted.json()["result"]["correct"] + submitted.json()["result"]["wrong"] + submitted.json()["result"]["blank"] == 40
        assert len(submitted.json()["result"]["questions"]) == 40
        assert all("correct" in item and "isCorrect" in item for item in submitted.json()["result"]["questions"])
        repeated_submit = user_client.post(f"/api/challenges/{challenge_date}/submit", json={"answers": [1] * 40})
        assert repeated_submit.status_code == 200
        assert repeated_submit.json()["result"]["score"] == submitted.json()["result"]["score"]
        assert user_client.put(f"/api/challenges/{challenge_date}/answers", json={"answers": [1] * 40}).json()["status"] == "completed"

        challenge_dashboard = admin_client.get("/api/admin/dashboard").json()
        assert challenge_dashboard["summary"]["minimumChallenges"] == 5
        assert challenge_dashboard["summary"]["attempts"] == 0
        assert challenge_dashboard["summary"]["participants"] == 0
        assert challenge_dashboard["summary"]["averageAttemptScore"] is None
        assert challenge_dashboard["types"][0]["count"] == 0

        ranking = admin_client.get(f"/api/challenges/{challenge_date}/leaderboard")
        assert ranking.json()["theoreticalCutoff"] == 16.25
        assert ranking.status_code == 200
        assert ranking.json()["participants"] == 1
        assert ranking.json()["entries"][0]["displayName"] == "Mario Rossi"
        assert ranking.json()["entries"][0]["rank"] == 1
        attempt_id = ranking.json()["entries"][0]["attemptId"]
        moderator_today = moderator_client.get("/api/challenges/today")
        assert moderator_today.status_code == 200
        assert moderator_today.json()["leaderboard"]["entries"][0]["attemptId"] == attempt_id
        assert moderator_client.get(f"/api/admin/challenges/{challenge_date}/attempts/{attempt_id}").status_code == 200
        assert moderator_client.delete(f"/api/admin/dashboard/challenges/{attempt_id}").status_code == 403
        assert "attemptId" not in user_client.get(f"/api/challenges/{challenge_date}/leaderboard").json()["entries"][0]
        assert user_client.get(f"/api/admin/challenges/{challenge_date}/attempts/{attempt_id}").status_code == 403
        opened_attempt = admin_client.get(f"/api/admin/challenges/{challenge_date}/attempts/{attempt_id}")
        assert opened_attempt.status_code == 200
        assert opened_attempt.json()["participant"]["username"] == "mario.rossi"
        assert len(opened_attempt.json()["result"]["questions"]) == 40
        assert opened_attempt.json()["result"]["score"] == submitted.json()["result"]["score"]
        assert opened_attempt.json()["result"]["questions"][0]["questionNumber"] == 1
        assert opened_attempt.json()["result"]["questions"][0]["responseSeconds"] == 1
        assert opened_attempt.json()["result"]["questions"][39]["responseSeconds"] == 40
        avatar_url = ranking.json()["entries"][0]["avatarUrl"].removeprefix(".")
        assert avatar_url == f"/api/users/{user_id}/avatar"
        default_avatar = user_client.get(avatar_url)
        assert default_avatar.status_code == 200
        assert default_avatar.headers["content-type"].startswith("image/jpeg")
        assert default_avatar.content == DEFAULT_AVATAR_BYTES
        assert public_client.get(avatar_url).status_code == 401
        assert user_client.get(avatar_url, headers={"If-None-Match": default_avatar.headers["etag"]}).status_code == 304
        avatar_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        assert user_client.put("/api/auth/avatar", json={"data_url": "data:image/png;base64,non-valida"}).status_code == 422
        avatar_update = user_client.put("/api/auth/avatar", json={"data_url": avatar_data})
        assert avatar_update.status_code == 200
        assert avatar_update.json()["avatarUrl"].startswith(f"./api/users/{user_id}/avatar?v=")
        custom_avatar = user_client.get(avatar_url)
        assert custom_avatar.headers["content-type"].startswith("image/png")
        assert custom_avatar.content.startswith(b"\x89PNG")
        personal_export_with_avatar = user_client.get("/api/account/data-export").json()
        assert personal_export_with_avatar["profilePhoto"]["mime"] == "image/png"
        assert personal_export_with_avatar["profilePhoto"]["dataUrl"] == avatar_data
        removed_avatar = user_client.delete("/api/auth/avatar")
        assert removed_avatar.status_code == 200
        assert user_client.get(avatar_url).content == DEFAULT_AVATAR_BYTES
        assert user_client.put("/api/auth/avatar", json={"data_url": avatar_data}).status_code == 200
        challenge_state = user_client.get("/api/auth/me").json()["user"]["state"]
        assert challenge_state["sessions"][-1]["type"] == "daily-challenge"
        assert challenge_state["dailyChallengeRecordedDates"] == [challenge_date]
        challenge_stats = admin_client.get(f"/api/admin/users/{user_id}/statistics").json()["summary"]
        assert challenge_stats["dailyChallenges"] == 1
        assert challenge_stats["fortyQuizzes"] == 3

        reported_question_id = original_challenge_ids[0]
        correction_url = f"/api/admin/questions/{reported_question_id}/correction"
        original_question = admin_client.get(correction_url).json()["question"]
        changed_index = (original_question["correct"] + 1) % len(original_question["answers"])
        corrected_answers = [f"{answer} (revisionata {index + 1})" for index, answer in enumerate(original_question["answers"])]
        correction = {"text": "Testo corretto della domanda.", "answers": corrected_answers, "correct": changed_index, "explanation": "Spiegazione verificata dall’amministratore.", "reason": "Correzione soluzione errata"}
        assert user_client.put(correction_url, json=correction).status_code == 403
        assert moderator_client.get(correction_url).status_code == 200
        assert moderator_client.put(correction_url, json=correction).status_code == 200
        assert admin_client.put(correction_url, json={**correction, "correct": 999}).status_code == 422
        assert admin_client.put(correction_url, json={**correction, "correct": True}).status_code == 422
        assert admin_client.put(correction_url, json=correction).status_code == 200
        assert admin_client.get(correction_url).json()["question"]["correct"] == changed_index
        assert admin_client.get(correction_url).json()["question"]["answers"] == corrected_answers
        assert admin_client.put(correction_url, json={**correction, "answers": ["Duplicata", " duplicata "]}).status_code == 422
        assert admin_client.put(correction_url, json={**correction, "answers": ["Valida", " "]}).status_code == 422
        assert user_client.get("/api/questions/availability").json()["corrections"][reported_question_id]["correct"] == changed_index
        with SessionLocal() as db:
            from cloud.app import DailyChallenge, challenge_questions, questions_by_id
            assert next(q for q in available_question_bank(db) if q["id"] == reported_question_id)["correct"] == changed_index
            old_challenge = db.get(DailyChallenge, challenge_today())
            assert challenge_questions(old_challenge)[0]["correct"] == original_question["correct"]
            assert questions_by_id[reported_question_id]["correct"] == original_question["correct"]
            future_challenge = build_daily_challenge(challenge_today() + timedelta(days=1), db)
            assert len(future_challenge.composition["solutions"]) == 40
            if reported_question_id in future_challenge.question_ids:
                assert future_challenge.composition["solutions"][reported_question_id]["answers"] == corrected_answers
        challenge_after_correction = user_client.get("/api/challenges/today").json()
        assert "solutions" not in challenge_after_correction["composition"]
        assert challenge_after_correction["result"]["questions"][0]["correct"] == original_question["correct"]
        assert challenge_after_correction["result"]["questions"][0]["text"] == original_question["text"]
        assert challenge_after_correction["result"]["questions"][0]["answers"] == original_question["answers"]
        assert admin_client.get(correction_url).json()["question"]["text"] == correction["text"]
        # Explicit rescoring changes both directions, without rewriting answers/timing/progress.
        before_rescore = user_client.get("/api/challenges/today").json()["result"]
        assert admin_client.put(correction_url, json={**correction, "rescore_today": True}).status_code == 409
        with patch("cloud.app.CHALLENGE_SECONDS", 0):
            progress_before = user_client.get("/api/auth/me").json()["user"]["state"]["progress"]
            reordered_answers = list(reversed(original_question["answers"]))
            assert admin_client.put(correction_url, json={**correction, "answers": reordered_answers, "rescore_today": True}).status_code == 422
            assert admin_client.put(correction_url, json={**correction, "rescore_today": True}).status_code == 200
            assert user_client.get("/api/challenges/today").json()["result"]["questions"][0]["answers"] == corrected_answers
            rescoring = {**correction, "answers": original_question["answers"], "rescore_today": True}
            assert moderator_client.put(correction_url, json=rescoring).status_code == 200
            applied = admin_client.put(correction_url, json=rescoring)
            assert applied.status_code == 200
            assert applied.json()["rescoredAttempts"] >= 1
            after_rescore = user_client.get("/api/challenges/today").json()["result"]
            rows = after_rescore["questions"]
            expected_correct = sum(row["isCorrect"] for row in rows)
            expected_wrong = sum(not row["blank"] and not row["isCorrect"] for row in rows)
            assert after_rescore["score"] == round(expected_correct - expected_wrong * .33, 2)
            assert [row["choice"] for row in rows] == [row["choice"] for row in before_rescore["questions"]]
            assert user_client.get("/api/auth/me").json()["user"]["state"]["progress"] == progress_before
            assert admin_client.put(correction_url, json=rescoring).status_code == 200
            assert user_client.get("/api/challenges/today").json()["result"]["score"] == after_rescore["score"]
            assert admin_client.put(correction_url, json={**rescoring, "correct": original_question["correct"]}).status_code == 200
            assert user_client.get("/api/challenges/today").json()["result"]["score"] == before_rescore["score"]
            assert admin_client.put(correction_url, json={**rescoring, "text": original_question["text"], "correct": original_question["correct"]}).status_code == 200
            assert admin_client.put(correction_url, json=correction).status_code == 200
            report_payload = {"question_id": reported_question_id, "reason": "answer", "note": "La soluzione indicata sembra errata."}
            reported = user_client.post("/api/question-reports", json=report_payload)
        assert reported.status_code == 201
        assert reported.json()["duplicate"] is False
        report_id = reported.json()["report"]["id"]
        duplicate = user_client.post("/api/question-reports", json=report_payload)
        assert duplicate.status_code == 200
        assert duplicate.json()["duplicate"] is True
        assert duplicate.json()["report"]["id"] == report_id
        assert user_client.get("/api/admin/question-reports").status_code == 403
        moderation = admin_client.get("/api/admin/question-reports")
        assert moderation.status_code == 200
        assert moderator_client.get("/api/admin/question-reports").status_code == 200
        assert moderation.json()["pendingCount"] == 1
        assert moderation.json()["pending"][0]["question"]["id"] == reported_question_id
        assert "correct" in moderation.json()["pending"][0]["question"]
        unrated = user_client.get(f"/api/question-ratings?question_ids={reported_question_id}")
        assert unrated.status_code == 200
        assert unrated.json()["ratings"][0] == {"questionId": reported_question_id, "average": None, "count": 0, "userRating": None}
        assert user_client.put(f"/api/question-ratings/{reported_question_id}", json={"rating": 0}).status_code == 422
        first_rating = user_client.put(f"/api/question-ratings/{reported_question_id}", json={"rating": 1})
        assert first_rating.status_code == 200
        assert first_rating.json()["rating"]["average"] == 1.0
        admin_rating = admin_client.put(f"/api/question-ratings/{reported_question_id}", json={"rating": 3})
        assert admin_rating.status_code == 200
        community = user_client.get(f"/api/question-ratings?question_ids={reported_question_id}").json()["ratings"][0]
        assert community["average"] == 2.0 and community["count"] == 2 and community["userRating"] == 1
        updated_rating = user_client.put(f"/api/question-ratings/{reported_question_id}", json={"rating": 2}).json()["rating"]
        assert updated_rating["average"] == 2.5 and updated_rating["count"] == 2 and updated_rating["userRating"] == 2
        personal_export = user_client.get("/api/account/data-export").json()
        assert personal_export["questionDifficultyRatings"][0]["questionId"] == reported_question_id
        assert personal_export["questionDifficultyRatings"][0]["rating"] == 2
        assert user_client.get('/api/question-reports/replies').json()['replies'] == []
        assert user_client.post(f'/api/admin/question-reports/{report_id}/dismiss', json={'reply': 'Non autorizzato'}).status_code == 403
        assert admin_client.post(f'/api/admin/question-reports/{report_id}/dismiss', json={'reply': 'x' * 4001}).status_code == 422
        reply_text = 'Il quesito è corretto: ecco i passaggi della soluzione.\nSecondo passaggio.'
        dismissed = moderator_client.post(f"/api/admin/question-reports/{report_id}/dismiss", json={'reply': reply_text})
        assert dismissed.status_code == 200
        assert dismissed.json()["report"]["status"] == "dismissed"
        assert dismissed.json()["report"]["reviewedBy"] == "Moderatore Test"
        history = moderator_client.get("/api/admin/question-reports").json()["history"]
        assert history[0]["id"] == report_id and history[0]["reviewedBy"] == "Moderatore Test"
        inbox = user_client.get('/api/question-reports/replies').json()['replies']
        assert len(inbox) == 1
        assert inbox[0]['reply'] == reply_text
        assert inbox[0]['question']['id'] == reported_question_id
        assert admin_client.get('/api/question-reports/replies').json()['replies'] == []
        assert admin_client.post(f'/api/question-reports/{report_id}/read').status_code == 404
        assert user_client.post(f'/api/question-reports/{report_id}/read').status_code == 200
        assert user_client.post(f'/api/question-reports/{report_id}/read').status_code == 200
        assert user_client.get('/api/question-reports/replies').json()['replies'] == []
        admin_client.post(f'/api/admin/question-reports/{report_id}/dismiss', json={'reply': 'Non sovrascrivere'})
        assert user_client.get('/api/question-reports/replies').json()['replies'] == []
        reported_again = user_client.post("/api/question-reports", json={**report_payload, "reason": "explanation"})
        assert reported_again.status_code == 201
        disabled = admin_client.post(
            f"/api/admin/questions/{reported_question_id}/disable",
            json={"reason": "Quesito in revisione dopo segnalazione."},
        )
        assert disabled.status_code == 200
        assert disabled.json()["currentChallengesPreserved"] is True
        assert disabled.json()["reportsResolved"] == 1
        accepted_reply = user_client.get('/api/question-reports/replies').json()['replies'][0]
        assert accepted_reply['status'] == 'resolved'
        assert 'accolta' in accepted_reply['reply']
        assert user_client.post("/api/question-reports", json=report_payload).status_code == 409
        assert user_client.put(f"/api/question-ratings/{reported_question_id}", json={"rating": 1}).status_code == 409
        availability = user_client.get("/api/questions/availability")
        assert availability.status_code == 200
        assert reported_question_id in availability.json()["disabledQuestionIds"]
        with SessionLocal() as moderation_db:
            assert reported_question_id not in {str(item["id"]) for item in available_question_bank(moderation_db)}
            future_challenge = build_daily_challenge(challenge_today() + timedelta(days=1), moderation_db)
            assert reported_question_id not in future_challenge.question_ids

        future_challenge_config = {
            "examPlan": {"storia": 9, "logica": 11, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4},
            "logicPlan": {"deduzioni": 2, "serie": 2, "verbale": 2, "calcolo": 1, "figure": 1, "insiemi": 1, "relazioni": 1, "ordinamenti": 1, "brani": 5, "mista": 0},
        }
        challenge_settings = admin_client.put(
            "/api/admin/challenge-settings",
            json={"enabled": True, "required": False, "config": future_challenge_config},
        )
        assert user_client.put("/api/admin/challenge-settings", json={"enabled": True, "config": future_challenge_config}).status_code == 403
        assert challenge_settings.status_code == 200
        assert challenge_settings.json()["currentChallengePreserved"] is True
        assert challenge_settings.json()["config"]["logicPlan"]["brani"] == 0
        assert sum(challenge_settings.json()["config"]["examPlan"].values()) == 40
        preserved_challenge = user_client.get("/api/challenges/today")
        assert preserved_challenge.status_code == 200
        assert preserved_challenge.json()["composition"] == original_challenge_composition
        assert [item["id"] for item in preserved_challenge.json()["result"]["questions"]] == original_challenge_ids
        assert preserved_challenge.json()["leaderboard"]["participants"] == 1
        assert reported_question_id in [item["id"] for item in preserved_challenge.json()["result"]["questions"]]
        assert admin_client.get("/api/admin/settings").json()["dailyChallengeConfig"] == challenge_settings.json()["config"]

        bank_settings = admin_client.put(
            "/api/admin/additional-banks",
            json={"nissolinoHistory": False, "modernHistory": True},
        )
        assert user_client.put("/api/admin/additional-banks", json={"nissolinoHistory": True, "modernHistory": True}).status_code == 403
        assert bank_settings.status_code == 200
        assert bank_settings.json()["currentChallengePreserved"] is True
        assert bank_settings.json()["additionalQuestionBanks"] == {"nissolinoHistory": False, "modernHistory": True}
        assert public_client.get("/api/runtime").json()["additionalQuestionBanks"] == {"nissolinoHistory": False, "modernHistory": True}
        with SessionLocal() as bank_db:
            forty_ids = {str(item["id"]) for item in available_forty_question_bank(bank_db)}
            assert not any(question_id.startswith("simone-history-") for question_id in forty_ids)
            assert any(question_id.startswith("modern-history-1990-2026-") for question_id in forty_ids)
        challenge_after_bank_change = user_client.get("/api/challenges/today").json()
        assert [item["id"] for item in challenge_after_bank_change["result"]["questions"]] == original_challenge_ids

        logo_data = avatar_data
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
            "daily_challenge_enabled": False,
            "daily_challenge_required": False,
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
        assert settings.json()["dailyChallengeConfig"] == challenge_settings.json()["config"]
        assert "token-segreto-test" not in settings.text
        assert "smtp-secret-test" not in settings.text
        assert public_client.get("/api/internal/tls-allowed?domain=quiz-test.duckdns.org").status_code == 204
        assert public_client.get("/api/internal/tls-allowed?domain=evil.example.com").status_code == 403
        assert public_client.get("/api/runtime").json()["registrationEnabled"] is False
        assert public_client.get("/api/runtime").json()["dailyChallengeEnabled"] is False
        assert user_client.get("/api/challenges/today").status_code == 404
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
        assert update_status.json()["currentVersion"] == "3.37.0"
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
        assert backup.json()["version"] == 6
        assert len(backup.json()["users"]) == 3
        backup_mario = next(item for item in backup.json()["users"] if item["id"] == user_id)
        assert backup_mario["avatar"]["mime"] == "image/png"
        assert len(backup.json()["dailyChallenges"]) == 1
        assert len(backup.json()["dailyChallengeAttempts"]) == 2
        assert len(backup.json()["questionReports"]) == 2
        assert backup.json()["disabledQuestions"][0]["questionId"] == reported_question_id
        assert backup.json()["settings"]["question_corrections"][reported_question_id]["correct"] == changed_index
        assert all("dailyChallengeRequired" in item for item in backup.json()["users"])
        assert all("activeChallengeMonitorEnabled" in item for item in backup.json()["users"])
        assert all("forcedChallengeDate" in item for item in backup.json()["users"])
        assert len(backup.json()["questionRatings"]) == 2
        backed_reply = next(r for r in backup.json()['questionReports'] if r['id'] == report_id)
        assert backed_reply['reply'] == reply_text
        assert backed_reply['replyReadAt'] is not None
        enabled = admin_client.delete(f"/api/admin/questions/{reported_question_id}/disable")
        assert enabled.status_code == 200
        assert reported_question_id not in admin_client.get("/api/questions/availability").json()["disabledQuestionIds"]

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
        restored = admin_client.post("/api/admin/restore", json=backup.json(), headers={"X-Confirm-Restore": "RESTORE"})
        assert restored.status_code == 204
        restored_admin = TestClient(app)
        assert login(restored_admin, "admin", "Admin-Sicura-2026!").status_code == 200
        restored_user = TestClient(app)
        assert login(restored_user, "mario.rossi", "Mario-Nuova-2026!").status_code == 200
        assert restored_user.get(avatar_url).headers["content-type"].startswith("image/png")
        restored_moderation = restored_admin.get("/api/admin/question-reports")
        assert len(restored_moderation.json()["pending"]) == 0
        assert restored_moderation.json()["disabled"][0]["questionId"] == reported_question_id
        assert restored_admin.get(correction_url).json()["question"]["correct"] == changed_index
        assert restored_admin.get(correction_url).json()["disabled"] is True
        saved = restored_admin.put(correction_url, json={**correction, "text": "Domanda revisionata", "reactivate": False})
        assert saved.status_code == 200
        assert restored_admin.get(correction_url).json()["disabled"] is True
        assert restored_admin.get(correction_url).json()["question"]["text"] == "Domanda revisionata"
        invalid = restored_admin.put(correction_url, json={**correction, "text": "   ", "reactivate": True})
        assert invalid.status_code == 422
        assert restored_admin.get(correction_url).json()["disabled"] is True
        activated = restored_admin.put(correction_url, json={**correction, "reactivate": True})
        assert activated.status_code == 200
        assert restored_admin.get(correction_url).json()["disabled"] is False
        assert reported_question_id not in restored_user.get('/api/questions/availability').json()['disabledQuestionIds']
        candidate_challenges = restored_admin.get(f"/api/admin/dashboard/candidates/{user_id}/challenges")
        assert candidate_challenges.status_code == 200
        assert len(candidate_challenges.json()["attempts"]) == 1
        saved_attempt = candidate_challenges.json()["attempts"][0]
        assert saved_attempt["date"] == challenge_date
        assert saved_attempt["score"] == submitted.json()["result"]["score"]
        assert restored_user.get(f"/api/admin/dashboard/candidates/{user_id}/challenges").status_code == 403
        forced = restored_admin.post(
            f"/api/moderation/challenges/{saved_attempt['id']}/force-redo",
            json={"reason": "Prova consegnata senza partecipazione effettiva."},
        )
        assert forced.status_code == 200
        assert forced.json()["challengeGate"]["forcedRedo"] is True
        assert forced.json()["challengeGate"]["completed"] is False
        assert restored_admin.get(f"/api/admin/dashboard/candidates/{user_id}/challenges").json()["attempts"] == []
        forced_me = restored_user.get("/api/auth/me").json()
        assert forced_me["challengeGate"]["required"] is True
        assert forced_me["challengeGate"]["forcedReason"] == "Prova consegnata senza partecipazione effettiva."
        assert forced_me["challengeGate"]["forcedBy"] == "Amministratore Test"
        assert forced_me["user"]["state"]["challengeRetryNotice"]["title"] == "La tua Sfida del giorno è stata invalidata"
        assert challenge_date not in forced_me["user"]["state"]["dailyChallengeRecordedDates"]

        forced_start = restored_user.post("/api/challenges/today/start", json={})
        assert forced_start.status_code == 200
        forced_attempt_id = next(
            item["id"] for item in restored_admin.get("/api/moderation/active-challenges").json()["attempts"]
            if item["username"] == "mario.rossi"
        )
        restored_moderator = TestClient(app)
        assert login(restored_moderator, "moderatore", "Moderatore-2026!").status_code == 200
        forced_again = restored_moderator.post(
            f"/api/moderation/challenges/{forced_attempt_id}/force-redo",
            json={"reason": "Avanzamento anomalo delle domande."},
        )
        assert forced_again.status_code == 200
        assert restored_user.post("/api/moderation/challenges/inesistente/force-redo", json={"reason": "No"}).status_code == 403
        forced_start = restored_user.post("/api/challenges/today/start", json={})
        incomplete = restored_user.post(
            f"/api/challenges/{challenge_date}/submit",
            json={"answers": [0] * 39 + [None], "questionSeconds": [1] * 40},
        )
        assert incomplete.status_code == 422
        assert restored_user.get("/api/auth/me").json()["challengeGate"]["forcedRedo"] is True
        completed_redo = restored_user.post(
            f"/api/challenges/{challenge_date}/submit",
            json={"answers": [0] * 40, "questionSeconds": [1] * 40},
        )
        assert completed_redo.status_code == 200
        assert completed_redo.json()["status"] == "completed"
        completed_gate = restored_user.get("/api/auth/me").json()["challengeGate"]
        assert completed_gate["forcedRedo"] is False
        assert completed_gate["completed"] is True
        assert restored_admin.get("/api/admin/dashboard").json()["summary"]["attempts"] == 0
