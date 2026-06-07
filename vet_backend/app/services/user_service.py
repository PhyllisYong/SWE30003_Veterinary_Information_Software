from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pet import Pet
from app.models.user import User
from app.repositories import user_repository, pet_repository
from app.schemas.pet import PetCreate, PetUpdate
from app.schemas.user import UpdateProfileRequest
from app.services.authentication import authentication


def register(db: Session, body) -> User:
    if user_repository.getByEmail(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashedPw = authentication.hashPassword(body.password)

    if body.role == "pet_owner":
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashedPw,
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
            password=hashedPw,
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
            password=hashedPw,
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
    user = user_repository.getByEmail(db, body.email)
    if user is None or not authentication.verifyPassword(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


def getProfile(db: Session, currentUser: User) -> dict:
    result = {
        "userID": currentUser.userID,
        "name": currentUser.name,
        "email": currentUser.email,
        "role": currentUser.role,
    }
    if currentUser.role == "pet_owner":
        owner = user_repository.getPetOwner(db, currentUser.userID)
        result["contactNumber"] = owner.contactNumber if owner else None
    elif currentUser.role == "veterinarian":
        vet = user_repository.getVeterinarian(db, currentUser.userID)
        result["licenseNumber"] = vet.licenseNumber if vet else None
        result["specialisation"] = vet.specialisation if vet else None
    elif currentUser.role == "association_admin":
        admin = user_repository.getAssociationAdmin(db, currentUser.userID)
        result["workID"] = admin.workID if admin else None
    return result


def updateProfile(db: Session, currentUser: User, body: UpdateProfileRequest) -> None:
    currentUser.updateProfile(name=body.name, email=body.email)

    if body.contactNumber and currentUser.role == "pet_owner":
        owner = user_repository.getPetOwner(db, currentUser.userID)
        if owner:
            owner.contactNumber = body.contactNumber

    if body.specialisation is not None and currentUser.role == "veterinarian":
        vet = user_repository.getVeterinarian(db, currentUser.userID)
        if vet:
            vet.specialisation = body.specialisation

    user_repository.update(db, currentUser)


def deleteAccount(db: Session, currentUser: User) -> None:
    authentication.invalidateSession(currentUser.userID)
    user_repository.deleteCascade(db, currentUser)


def getUsersByRole(db: Session, role: str) -> list[User]:
    return user_repository.getAllByRole(db, role)


def getPets(db: Session, ownerId: str) -> list[Pet]:
    return pet_repository.getByOwner(db, ownerId)


def createPet(db: Session, ownerId: str, body: PetCreate) -> Pet:
    pet = Pet(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
        petOwnerID=ownerId,
    )
    return pet_repository.add(db, pet)


def getPetByIdAndOwner(db: Session, petId: str, ownerId: str) -> Pet:
    pet = pet_repository.getByIdAndOwner(db, petId, ownerId)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


def updatePet(db: Session, petId: str, ownerId: str, body: PetUpdate) -> Pet:
    pet = getPetByIdAndOwner(db, petId, ownerId)
    pet.updatePetDetails(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
    )
    return pet_repository.update(db, pet)


def deletePet(db: Session, petId: str, ownerId: str) -> None:
    pet = getPetByIdAndOwner(db, petId, ownerId)
    pet_repository.delete(db, pet)
