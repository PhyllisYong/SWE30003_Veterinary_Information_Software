"""
Seed demo users for each role plus a small set of pets.

Run from vet_backend/:
    python -m seeds.seed_users

All seeded users use password: Password123!
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.association_admin import AssociationAdministrator
from app.models.pet import Pet
from app.models.pet_owner import PetOwner
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.services.authentication import authentication


PASSWORD = "Password123!"

USERS = [
    {
        "name": "Lily",
        "email": "lily.owner@example.com",
        "role": "pet_owner",
        "contactNumber": "+60 12-345 6789",
        "pets": [
            {"petName": "Milo", "petType": "dog", "age": 4, "gender": "male"},
            {"petName": "Luna", "petType": "cat", "age": 3, "gender": "female"},
            {"petName": "Coco", "petType": "guinea_pig", "age": 2, "gender": "female"},
        ],
    },
    {
        "name": "Aminah Rahman",
        "email": "aminah.owner@example.com",
        "role": "pet_owner",
        "contactNumber": "+60 13-222 3344",
        "pets": [
            {"petName": "BunBun", "petType": "rabbit", "age": 2, "gender": "female"},
            {"petName": "Nibbles", "petType": "hamster", "age": 1, "gender": "male"},
        ],
    },
    {
        "name": "Dr. Ann Morgan",
        "email": "ann.vet@example.com",
        "role": "veterinarian",
        "licenseNumber": "VET-001",
        "specialisation": "Emergency and Critical Care",
        "availableSlots": [
            "2026-06-01T09:00:00Z",
            "2026-06-01T10:00:00Z",
            "2026-06-02T14:00:00Z",
        ],
    },
    {
        "name": "Dr. Ravi Kumar",
        "email": "ravi.vet@example.com",
        "role": "veterinarian",
        "licenseNumber": "VET-002",
        "specialisation": "Small Animal Medicine",
        "availableSlots": [
            "2026-06-03T09:30:00Z",
            "2026-06-03T11:00:00Z",
            "2026-06-04T15:30:00Z",
        ],
    },
    {
        "name": "Nora Admin",
        "email": "nora.admin@example.com",
        "role": "association_admin",
        "workID": "ADMIN-001",
    },
    {
        "name": "Joshua Admin",
        "email": "joshua.admin@example.com",
        "role": "association_admin",
        "workID": "ADMIN-002",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        pet_count = 0
        password_hash = authentication.hash_password(PASSWORD)

        for data in USERS:
            existing = db.query(User).filter(User.email == data["email"]).first()
            if existing:
                continue

            if data["role"] == "pet_owner":
                user = PetOwner(
                    name=data["name"],
                    email=data["email"],
                    password=password_hash,
                    role="pet_owner",
                    contactNumber=data["contactNumber"],
                )
            elif data["role"] == "veterinarian":
                user = Veterinarian(
                    name=data["name"],
                    email=data["email"],
                    password=password_hash,
                    role="veterinarian",
                    licenseNumber=data["licenseNumber"],
                    specialisation=data["specialisation"],
                    availableSlots=data["availableSlots"],
                )
            else:
                user = AssociationAdministrator(
                    name=data["name"],
                    email=data["email"],
                    password=password_hash,
                    role="association_admin",
                    workID=data["workID"],
                )

            db.add(user)
            db.flush()
            created += 1

            for pet_data in data.get("pets", []):
                db.add(Pet(ownerID=user.userID, **pet_data))
                pet_count += 1

        db.commit()
        print(f"Seeded {created} users and {pet_count} pets")
        print(f"Password for all seeded users: {PASSWORD}")

    except Exception as e:
        db.rollback()
        print(f"Seed users failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
