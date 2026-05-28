from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.models.pet_owner import PetOwner
from app.models.veterinarian import Veterinarian
from app.models.association_admin import AssociationAdministrator
from app.models.booking import Booking
from app.models.chat import VeterinaryAdviceChat
from app.models.first_aid_content import FirstAidContent
from app.models.message import Message
from app.models.pet import Pet
from app.models.quiz_result import QuizResult
from app.schemas.user import UpdateProfileRequest
from app.schemas.pet import PetCreate, PetUpdate, PetResponse
from app.services.authentication import authentication

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
    current_user.updateProfile(name=body.name, email=body.email)

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


# DELETE /api/profile
@router.delete("/profile")
def delete_profile(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db)
):
    user_id = current_user.userID

    db.query(FirstAidContent).filter(
        FirstAidContent.authorVetID == user_id
    ).update({FirstAidContent.authorVetID: None}, synchronize_session=False)
    db.query(FirstAidContent).filter(
        FirstAidContent.assignedVetID == user_id
    ).update({FirstAidContent.assignedVetID: None}, synchronize_session=False)

    if current_user.role == "pet_owner":
        chat_ids = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.petOwnerID == user_id
            ).all()
        ]
        if chat_ids:
            db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                synchronize_session=False
            )
        db.query(QuizResult).filter(QuizResult.petOwnerID == user_id).delete(
            synchronize_session=False
        )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.petOwnerID == user_id
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.petOwnerID == user_id).delete(
            synchronize_session=False
        )
        db.query(Pet).filter(Pet.ownerID == user_id).delete(synchronize_session=False)

    if current_user.role == "veterinarian":
        chat_ids = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.vetID == user_id
            ).all()
        ]
        if chat_ids:
            db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                synchronize_session=False
            )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.vetID == user_id
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.vetID == user_id).delete(
            synchronize_session=False
        )

    authentication.invalidateSession(user_id)
    db.delete(current_user)
    db.commit()
    return {"status": "ok", "data": {"message": "Account deleted successfully"}}


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

    pet.updatePetDetails(
        petName=body.petName,
        petType=body.petType,
        age=body.age,
        gender=body.gender,
    )

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

    db.query(Booking).filter(Booking.petID == pet.petID).update(
        {Booking.petID: None},
        synchronize_session=False,
    )
    db.delete(pet)
    db.commit()
    return {"status": "ok", "data": {"message": "Pet deleted successfully"}}
