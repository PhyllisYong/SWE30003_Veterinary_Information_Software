"""
Clear all application data and reseed demo data.

Run from vet_backend/:
    python -m seeds.reset_all

This preserves alembic_version and only truncates application tables.
"""

import os
import sys
import argparse

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine
from seeds.seed_content import seed as seed_content
from seeds.seed_quiz import seed as seed_quiz
from seeds.seed_users import seed as seed_users


TABLES = [
    "answers",
    "quiz_results",
    "questions",
    "messages",
    "bookings",
    "vet_advice_chats",
    "pets",
    "guides",
    "videos",
    "quizzes",
    "first_aid_contents",
    "association_admins",
    "veterinarians",
    "pet_owners",
    "users",
]


def clear_all() -> None:
    table_list = ", ".join(TABLES)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))
    print("Cleared application tables")


def reset() -> None:
    clear_all()
    seed_users()
    seed_content()
    seed_quiz()
    print("Database reset and reseed complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear and reseed all application data.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that all application records should be deleted before reseeding.",
    )
    args = parser.parse_args()
    if not args.yes:
        raise SystemExit("Refusing to reset without --yes")
    reset()
