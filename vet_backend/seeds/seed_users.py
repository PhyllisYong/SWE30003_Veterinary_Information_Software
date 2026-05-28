"""
Seed script — creates three test accounts (pet owner, veterinarian, admin).
Run from vet_backend/:
    python -m seeds.seed_users

Credentials
-----------
  Pet owner   test_petowner@test.com   / Password123!
  Vet         test_vet@test.com        / Password123!
  Admin       test_admin@test.com      / Password123!
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.security import hashPassword
from app.models.pet_owner import PetOwner
from app.models.veterinarian import Veterinarian
from app.models.association_admin import AssociationAdministrator

TEST_PASSWORD = "Password123!"

USERS = [
    {
        "model": PetOwner,
        "kwargs": {
            "name": "Test PetOwner",
            "email": "test_petowner@test.com",
            "role": "pet_owner",
            "contactNumber": "0400000001",
        },
    },
    {
        "model": Veterinarian,
        "kwargs": {
            "name": "Test Vet",
            "email": "test_vet@test.com",
            "role": "veterinarian",
            "licenseNumber": "VET-TEST-001",
            "specialisation": "General Practice",
            "availableSlots": [],
        },
    },
    {
        "model": AssociationAdministrator,
        "kwargs": {
            "name": "Test Admin",
            "email": "test_admin@test.com",
            "role": "association_admin",
            "workID": "ADMIN-TEST-001",
        },
    },
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        hashed_pw = hashPassword(TEST_PASSWORD)

        for entry in USERS:
            email = entry["kwargs"]["email"]
            from app.models.user import User
            exists = db.query(User).filter(User.email == email).first()
            if exists:
                print(f"  skip  {email} (already exists)")
                skipped += 1
                continue

            user = entry["model"](password=hashed_pw, **entry["kwargs"])
            db.add(user)
            created += 1
            print(f"  add   {email}")

        db.commit()
        print(f"\nDone — {created} created, {skipped} skipped.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
