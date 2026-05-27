from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.models.pet_owner import PetOwner
from app.models.veterinarian import Veterinarian
from app.models.association_admin import AssociationAdministrator
from app.models.pet import Pet
from app.schemas.user import UpdateProfileRequest
from app.schemas.pet import PetCreate, PetUpdate, PetResponse

router = APIRouter(tags=["Profile & Pets"])


# GET /api/profile
@router.get("/profile")
def get_profile(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    result = {
        "userID": current_user.userID,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }
    if current_user.role == "pet_owner":
        owner = db.query(PetOwner).filter(PetOwner.userID == current_user.userID).first()
        result["contactNumber"] = owner.contactNumber if owner else None

    elif current_user.role == "veterinarian":
        vet = db.query(Veterinarian).filter(Veterinarian.userID == current_user.userID).first()
        result["licenseNumber"] = vet.licenseNumber if vet else None
        result["specialisation"] = vet.specialisation if vet else None

    elif current_user.role == "association_admin":
        admin = db.query(AssociationAdministrator).filter(
            AssociationAdministrator.userID == current_user.userID
        ).first()
        result["workID"] = admin.workID if admin else None

    return {"status": "ok", "data": result}


# PUT /api/profile
@router.put("/profile")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    if body.name:
        current_user.name = body.name
    if body.email:
        current_user.email = body.email

    if body.contactNumber and current_user.role == "pet_owner":
        owner = db.query(PetOwner).filter(PetOwner.userID == current_user.userID).first()
        if owner:
            owner.contactNumber = body.contactNumber

    if body.specialisation is not None and current_user.role == "veterinarian":
        vet = db.query(Veterinarian).filter(Veterinarian.userID == current_user.userID).first()
        if vet:
            vet.specialisation = body.specialisation

    db.commit()
    return {"status": "ok", "data": {"message": "Profile updated successfully"}}


# GET /api/pets
@router.get("/pets")
def get_pets(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can access pets")

    pets = db.query(Pet).filter(Pet.ownerID == current_user.userID).all()
    return {"status": "ok", "data": [PetResponse.model_validate(p) for p in pets]}


# POST /api/pets
@router.post("/pets")
def create_pet(
    body: PetCreate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can create pets")

    pet = Pet(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
        ownerID=current_user.userID
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# PUT /api/pets/{petID}
@router.put("/pets/{petID}")
def update_pet(
    petID: str,
    body: PetUpdate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    pet = db.query(Pet).filter(
        Pet.petID == petID,
        Pet.ownerID == current_user.userID
    ).first()

    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    if body.petName: pet.petName = body.petName
    if body.petType: pet.petType = body.petType
    if body.age:     pet.age = body.age
    if body.gender:  pet.gender = body.gender

    db.commit()
    db.refresh(pet)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# DELETE /api/pets/{petID}
@router.delete("/pets/{petID}")
def delete_pet(
    petID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    pet = db.query(Pet).filter(
        Pet.petID == petID,
        Pet.ownerID == current_user.userID
    ).first()

    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db.delete(pet)
    db.commit()
    return {"status": "ok", "data": {"message": "Pet deleted successfully"}}