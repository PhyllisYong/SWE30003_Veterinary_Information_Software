from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.services import booking_service

router = APIRouter(tags=["Booking"])


# GET /api/vets — list vets with available slots (for booking UI)
@router.get("/api/vets")
def list_vets(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    return {"status": "ok", "data": booking_service.list_vets(db)}


# PUT /api/vets/availability — setAvailability() [Vet only]
@router.put("/api/vets/availability")
def set_availability(
    slots: list[str],
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can set availability")
    available = booking_service.set_availability(db, current_user, slots)
    return {"status": "ok", "data": {"availableSlots": available}}


# POST /api/bookings — makeBooking() [PetOwner]
@router.post("/api/bookings")
def make_booking(
    body: BookingCreate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can make bookings")
    booking = booking_service.make_booking(db, current_user, body)
    return {"status": "ok", "data": booking}


# GET /api/bookings — list own bookings
@router.get("/api/bookings")
def list_bookings(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    return {"status": "ok", "data": booking_service.list_bookings(db, current_user)}


# PUT /api/bookings/{bookingID}/accept — acceptBooking() [Vet]
@router.put("/api/bookings/{bookingID}/accept")
def accept_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can accept bookings")
    booking = booking_service.accept_booking(db, bookingID, current_user)
    return {"status": "ok", "data": booking}


# PUT /api/bookings/{bookingID}/cancel — cancel by owner or vet
@router.put("/api/bookings/{bookingID}/cancel")
def cancel_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    booking = booking_service.cancel_booking(db, bookingID, current_user)
    return {"status": "ok", "data": booking}
