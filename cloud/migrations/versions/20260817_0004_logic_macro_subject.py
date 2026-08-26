"""Riunisce brani e insiemi nella macro-materia Logica.

Revision ID: 20260817_0004
Revises: 20260817_0003
"""

from copy import deepcopy

from alembic import op
import sqlalchemy as sa


revision = "20260817_0004"
down_revision = "20260817_0003"
branch_labels = None
depends_on = None


DEFAULT_EXAM_PLAN = {"storia": 8, "logica": 12, "fisica": 6, "chimica": 6, "informatica": 4, "inglese": 4}
DEFAULT_LOGIC_PLAN = {"deduzioni": 2, "serie": 2, "verbale": 2, "calcolo": 1, "figure": 1, "insiemi": 1, "relazioni": 1, "ordinamenti": 1, "brani": 0, "mista": 1}
LOGIC_TOPIC_IDS = tuple(DEFAULT_LOGIC_PLAN)


def whole(value: object) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def migrate_plan(raw_plan: object) -> tuple[dict[str, int], int, int, int]:
    plan = raw_plan if isinstance(raw_plan, dict) else {}
    legacy_logic = whole(plan.get("logica"))
    legacy_sets = whole(plan.get("insiemi"))
    legacy_passages = whole(plan.get("brani"))
    migrated = {key: whole(plan.get(key)) for key in DEFAULT_EXAM_PLAN}
    migrated["logica"] = legacy_logic + legacy_sets + legacy_passages
    return migrated, legacy_logic, legacy_sets, legacy_passages


def migrate_logic_plan(raw_logic_plan: object, legacy_logic: int, legacy_sets: int, legacy_passages: int, target: int) -> dict[str, int]:
    if not isinstance(raw_logic_plan, dict):
        return deepcopy(DEFAULT_LOGIC_PLAN) if target == 12 else {**{key: 0 for key in LOGIC_TOPIC_IDS}, "mista": target}
    migrated = {key: whole(raw_logic_plan.get(key)) for key in LOGIC_TOPIC_IDS}
    if (legacy_sets or legacy_passages) and sum(migrated.values()) == legacy_logic:
        migrated["insiemi"] += legacy_sets
        migrated["brani"] += legacy_passages
    difference = target - sum(migrated.values())
    if difference > 0:
        migrated["mista"] += difference
    return migrated


def migrate_config(value: object) -> object:
    if not isinstance(value, dict):
        return value
    migrated = deepcopy(value)
    plan, legacy_logic, legacy_sets, legacy_passages = migrate_plan(value.get("examPlan"))
    migrated["examPlan"] = plan
    migrated["logicPlan"] = migrate_logic_plan(value.get("logicPlan"), legacy_logic, legacy_sets, legacy_passages, plan["logica"])
    return migrated


def migrate_state(value: object) -> object:
    if not isinstance(value, dict):
        return value
    migrated = deepcopy(value)
    presets = migrated.get("examPresets")
    if isinstance(presets, list):
        for preset in presets:
            if not isinstance(preset, dict):
                continue
            plan, legacy_logic, legacy_sets, legacy_passages = migrate_plan(preset.get("plan"))
            preset["plan"] = plan
            preset["logicPlan"] = migrate_logic_plan(preset.get("logicPlan"), legacy_logic, legacy_sets, legacy_passages, plan["logica"])
    exposure = migrated.get("fortyQuestionExposure")
    if isinstance(exposure, dict):
        for old_key, new_key in (("insiemi", "logica:insiemi"), ("brani", "logica:brani")):
            if old_key in exposure and new_key not in exposure:
                exposure[new_key] = exposure.pop(old_key)
    return migrated


def upgrade() -> None:
    bind = op.get_bind()
    settings = sa.table("settings", sa.column("key", sa.String()), sa.column("value", sa.JSON()))
    current = bind.execute(sa.select(settings.c.value).where(settings.c.key == "exam_config")).scalar_one_or_none()
    if current is not None:
        bind.execute(settings.update().where(settings.c.key == "exam_config").values(value=migrate_config(current)))

    user_states = sa.table("user_states", sa.column("user_id", sa.String()), sa.column("data", sa.JSON()))
    for user_id, data in bind.execute(sa.select(user_states.c.user_id, user_states.c.data)):
        bind.execute(user_states.update().where(user_states.c.user_id == user_id).values(data=migrate_state(data)))


def downgrade() -> None:
    # La fusione conserva gli identificativi dei quesiti e non elimina progressi.
    # Non viene separata automaticamente per evitare di alterare preferenze salvate dopo l'upgrade.
    pass
