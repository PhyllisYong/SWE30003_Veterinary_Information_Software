from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.schemas.pet import PetCreate, PetUpdate, PetResponse
from app.schemas.user import UpdateProfileRequest
from app.services import user_service

router = APIRouter(tags=["Profile & Pets"])


# GET /api/profile
@router.get("/profile")
def get_profile(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    data = user_service.get_profile(db, current_user)
    return {"status": "ok", "data": data}


# PUT /api/profile
@router.put("/profile")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    user_service.update_profile(db, current_user, body)
    return {"status": "ok", "data": {"message": "Profile updated successfully"}}


# DELETE /api/profile
@router.delete("/profile")
def delete_profile(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    user_service.delete_account(db, current_user)
    return {"status": "ok", "data": {"message": "Account deleted successfully"}}


# GET /api/pets
@router.get("/pets")
def get_pets(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can access pets")
    pets = user_service.get_pets(db, current_user.userID)
    return {"status": "ok", "data": [PetResponse.model_validate(p) for p in pets]}


# POST /api/pets
@router.post("/pets")
def create_pet(
    body: PetCreate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can create pets")
    pet = user_service.create_pet(db, current_user.userID, body)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# PUT /api/pets/{petID}
@router.put("/pets/{petID}")
def update_pet(
    petID: str,
    body: PetUpdate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    pet = user_service.update_pet(db, petID, current_user.userID, body)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# DELETE /api/pets/{petID}
@router.delete("/pets/{petID}")
def delete_pet(
    petID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    user_service.delete_pet(db, petID, current_user.userID)
    return {"status": "ok", "data": {"message": "Pet deleted successfully"}}
