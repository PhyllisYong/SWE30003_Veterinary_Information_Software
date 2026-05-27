from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.models.booking import Booking
from app.models.veterinarian import Veterinarian
from app.schemas.booking import BookingCreate, BookingResponse, VetSlotResponse

router = APIRouter(tags=["Booking"])


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# GET /api/vets — list vets with available slots (for booking UI)
@router.get("/api/vets")
def list_vets(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    vets = db.query(Veterinarian).all()
    return {
        "status": "ok",
        "data": [
            VetSlotResponse(
                vetID=v.userID,
                name=v.name,
                specialisation=v.specialisation,
                availableSlots=v.availableSlots or [],
            )
            for v in vets
        ],
    }


# PUT /api/vets/availability — setAvailability() [Vet only]
@router.put("/api/vets/availability")
def set_availability(
    slots: list[str],
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can set availability")

    vet = db.query(Veterinarian).filter(Veterinarian.userID == current_user.userID).first()
    vet.availableSlots = slots
    db.commit()
    return {"status": "ok", "data": {"availableSlots": slots}}


# POST /api/bookings — makeBooking() [PetOwner]
@router.post("/api/bookings")
def make_booking(
    body: BookingCreate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can make bookings")

    vet = db.query(Veterinarian).filter(Veterinarian.userID == body.vetID).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    booking = Booking(
        createdAt=_now(),
        timeslot=body.timeslot,
        bookingStatus="pending",
        petOwnerID=current_user.userID,
        vetID=body.vetID,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"status": "ok", "data": BookingResponse.model_validate(booking)}


# GET /api/bookings — list own bookings
@router.get("/api/bookings")
def list_bookings(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role == "pet_owner":
        bookings = db.query(Booking).filter(Booking.petOwnerID == current_user.userID).all()
    elif current_user.role == "veterinarian":
        bookings = db.query(Booking).filter(Booking.vetID == current_user.userID).all()
    else:
        raise HTTPException(status_code=403, detail="Only pet owners and vets can view bookings")

    return {"status": "ok", "data": [BookingResponse.model_validate(b) for b in bookings]}


# PUT /api/bookings/{bookingID}/accept — acceptBooking() [Vet]
@router.put("/api/bookings/{bookingID}/accept")
def accept_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can accept bookings")

    booking = db.query(Booking).filter(
        Booking.bookingID == bookingID,
        Booking.vetID == current_user.userID,
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.bookingStatus != "pending":
        raise HTTPException(status_code=409, detail=f"Booking is already {booking.bookingStatus}")

    booking.updateStatus("accepted")
    db.commit()
    db.refresh(booking)
    return {"status": "ok", "data": BookingResponse.model_validate(booking)}


# PUT /api/bookings/{bookingID}/cancel — cancel by owner or vet
@router.put("/api/bookings/{bookingID}/cancel")
def cancel_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.bookingID == bookingID).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.userID not in (booking.petOwnerID, booking.vetID):
        raise HTTPException(status_code=403, detail="Not authorised to cancel this booking")

    if booking.bookingStatus == "completed":
        raise HTTPException(status_code=409, detail="Cannot cancel a completed booking")

    booking.updateStatus("cancelled")
    db.commit()
    db.refresh(booking)
    return {"status": "ok", "data": BookingResponse.model_validate(booking)}
