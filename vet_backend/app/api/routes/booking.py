from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import getDb
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.services import booking_service

router = APIRouter(tags=["Booking"])


# GET /api/vets — list vets with available slots (for booking UI)
@router.get("/api/vets")
def listVets(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    return {"status": "ok", "data": booking_service.listVets(db)}


# PUT /api/vets/availability — setAvailability() [Vet only]
@router.put("/api/vets/availability")
def setAvailability(
    availableSlots: list[str],
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    if currentUser.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can set availability")
    slots = booking_service.setAvailability(db, currentUser, availableSlots)
    return {"status": "ok", "data": {"availableSlots": slots}}


# POST /api/bookings — makeBooking() [PetOwner]
@router.post("/api/bookings")
def makeBooking(
    body: BookingCreate,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    if currentUser.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can make bookings")
    booking = booking_service.makeBooking(db, currentUser, body)
    return {"status": "ok", "data": booking}


# GET /api/bookings — list own bookings
@router.get("/api/bookings")
def listBookings(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    return {"status": "ok", "data": booking_service.listBookings(db, currentUser)}


# PUT /api/bookings/{bookingID}/accept — acceptBooking() [Vet]
@router.put("/api/bookings/{bookingID}/accept")
def acceptBooking(
    bookingID: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    if currentUser.role != "veterinarian":
        raise HTTPException(status_code=403, detail="Only veterinarians can accept bookings")
    booking = booking_service.acceptBooking(db, bookingID, currentUser)
    return {"status": "ok", "data": booking}


# PUT /api/bookings/{bookingID}/cancel — cancel by owner or vet
@router.put("/api/bookings/{bookingID}/cancel")
def cancelBooking(
    bookingID: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    booking = booking_service.cancelBooking(db, bookingID, currentUser)
    return {"status": "ok", "data": booking}
