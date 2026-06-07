from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import getDb
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.schemas.pet import PetCreate, PetUpdate, PetResponse
from app.schemas.user import UpdateProfileRequest
from app.services import user_service
from app.services.authentication import authentication

router = APIRouter(tags=["Profile & Pets"])


# GET /api/profile
@router.get("/profile")
def getProfile(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    data = user_service.getProfile(db, currentUser)
    return {"status": "ok", "data": data}


# PUT /api/profile
@router.put("/profile")
def updateProfile(
    body: UpdateProfileRequest,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    user_service.updateProfile(db, currentUser, body)
    return {"status": "ok", "data": {"message": "Profile updated successfully"}}


# DELETE /api/profile
@router.delete("/profile")
def deleteProfile(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    user_service.deleteAccount(db, currentUser)
    return {"status": "ok", "data": {"message": "Account deleted successfully"}}


# GET /api/pets
@router.get("/pets")
def getPets(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    if currentUser.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can access pets")
    pets = user_service.getPets(db, currentUser.userID)
    return {"status": "ok", "data": [PetResponse.model_validate(p) for p in pets]}


# POST /api/pets
@router.post("/pets")
def createPet(
    body: PetCreate,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    if currentUser.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can create pets")
    pet = user_service.createPet(db, currentUser.userID, body)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# PUT /api/pets/{petID}
@router.put("/pets/{petID}")
def updatePet(
    petID: str,
    body: PetUpdate,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    pet = user_service.updatePet(db, petID, currentUser.userID, body)
    return {"status": "ok", "data": PetResponse.model_validate(pet)}


# DELETE /api/pets/{petID}
@router.delete("/pets/{petID}")
def deletePet(
    petID: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    user_service.deletePet(db, petID, currentUser.userID)
    return {"status": "ok", "data": {"message": "Pet deleted successfully"}}
