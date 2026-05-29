from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pet import Pet
from app.models.user import User
from app.repositories import user_repository, pet_repository
from app.schemas.pet import PetCreate, PetUpdate
from app.schemas.user import UpdateProfileRequest
from app.services.authentication import authentication


def register(db: Session, body) -> User:
    if user_repository.get_by_email(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_pw = authentication.hash_password(body.password)

    if body.role == "pet_owner":
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="pet_owner",
            contactNumber=body.contactNumber,
        )
    elif body.role == "veterinarian":
        if not body.licenseNumber:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="licenseNumber is required for veterinarian registration",
            )
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="veterinarian",
            licenseNumber=body.licenseNumber,
            specialisation=body.specialisation,
        )
    elif body.role == "association_admin":
        if not body.workID:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="workID is required for association admin registration",
            )
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="association_admin",
            workID=body.workID,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be one of: pet_owner, veterinarian, association_admin",
        )

    return user_repository.add(db, user)


def login(db: Session, body) -> User:
    user = user_repository.get_by_email(db, body.email)
    if user is None or not authentication.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


def get_profile(db: Session, current_user: User) -> dict:
    result = {
        "userID": current_user.userID,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }
    if current_user.role == "pet_owner":
        owner = user_repository.get_pet_owner(db, current_user.userID)
        result["contactNumber"] = owner.contactNumber if owner else None
    elif current_user.role == "veterinarian":
        vet = user_repository.get_veterinarian(db, current_user.userID)
        result["licenseNumber"] = vet.licenseNumber if vet else None
        result["specialisation"] = vet.specialisation if vet else None
    elif current_user.role == "association_admin":
        admin = user_repository.get_association_admin(db, current_user.userID)
        result["workID"] = admin.workID if admin else None
    return result


def update_profile(db: Session, current_user: User, body: UpdateProfileRequest) -> None:
    current_user.updateProfile(name=body.name, email=body.email)

    if body.contactNumber and current_user.role == "pet_owner":
        owner = user_repository.get_pet_owner(db, current_user.userID)
        if owner:
            owner.contactNumber = body.contactNumber

    if body.specialisation is not None and current_user.role == "veterinarian":
        vet = user_repository.get_veterinarian(db, current_user.userID)
        if vet:
            vet.specialisation = body.specialisation

    user_repository.update(db, current_user)


def delete_account(db: Session, current_user: User) -> None:
    authentication.invalidateSession(current_user.userID)
    user_repository.delete_cascade(db, current_user)


def get_users_by_role(db: Session, role: str) -> list[User]:
    return user_repository.get_all_by_role(db, role)


def get_pets(db: Session, owner_id: str) -> list[Pet]:
    return pet_repository.get_by_owner(db, owner_id)


def create_pet(db: Session, owner_id: str, body: PetCreate) -> Pet:
    pet = Pet(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
        ownerID=owner_id,
    )
    return pet_repository.add(db, pet)


def get_pet_by_id_and_owner(db: Session, pet_id: str, owner_id: str) -> Pet:
    pet = pet_repository.get_by_id_and_owner(db, pet_id, owner_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


def update_pet(db: Session, pet_id: str, owner_id: str, body: PetUpdate) -> Pet:
    pet = get_pet_by_id_and_owner(db, pet_id, owner_id)
    pet.updatePetDetails(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
    )
    return pet_repository.update(db, pet)


def delete_pet(db: Session, pet_id: str, owner_id: str) -> None:
    pet = get_pet_by_id_and_owner(db, pet_id, owner_id)
    pet_repository.delete(db, pet)
