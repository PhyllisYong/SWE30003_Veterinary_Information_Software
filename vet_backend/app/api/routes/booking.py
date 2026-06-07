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
    return {"status": "ok", "data": booking_service.listVets(db)}


# PUT /api/vets/availability — setAvailability() [Vet only]
@router.put("/api/vets/availability")
def set_availability(
    availableSlots: list[str],
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can set availability")
    current_user.setAvailability(availableSlots)
    from app.repositories import booking_repository
    booking_repository.update_vet(db, current_user)
    return {"status": "ok", "data": {"availableSlots": availableSlots}}


# POST /api/bookings — makeBooking() [PetOwner]
@router.post("/api/bookings")
def make_booking(
    body: BookingCreate,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can make bookings")
    booking = current_user.makeBooking(db, body.veterinarianID, body.timeslot, body.petID)
    return {"status": "ok", "data": booking}


# GET /api/bookings — list own bookings
@router.get("/api/bookings")
def list_bookings(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    return {"status": "ok", "data": booking_service.listBookings(db, current_user)}


# PUT /api/bookings/{bookingID}/accept — acceptBooking() [Vet]
@router.put("/api/bookings/{bookingID}/accept")
def accept_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can accept bookings")
    booking = current_user.acceptBookingSlot(db, bookingID)
    return {"status": "ok", "data": booking}


# PUT /api/bookings/{bookingID}/cancel — cancel by owner or vet
@router.put("/api/bookings/{bookingID}/cancel")
def cancel_booking(
    bookingID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    booking = booking_service.cancelBooking(db, bookingID, current_user)
    return {"status": "ok", "data": booking}
