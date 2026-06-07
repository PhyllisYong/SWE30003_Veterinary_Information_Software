from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.repositories import booking_repository, pet_repository
from app.schemas.booking import BookingCreate, BookingResponse, VetSlotResponse


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bookingPayload(booking: Booking) -> BookingResponse:
    return BookingResponse(
        bookingID=booking.bookingID,
        createdAt=booking.createdAt,
        timeslot=booking.timeslot,
        bookingStatus=booking.bookingStatus,
        petOwnerID=booking.petOwnerID,
        veterinarianID=booking.veterinarianID,
        petID=booking.petID,
        petName=booking.pet.petName if booking.pet else None,
        petType=booking.pet.petType if booking.pet else None,
    )


def _restoreSlot(vet: Veterinarian, timeslot: str) -> None:
    slots = list(vet.availableSlots or [])
    if timeslot not in slots:
        slots.append(timeslot)
        slots.sort()
        vet.availableSlots = slots


def listVets(db: Session) -> list[VetSlotResponse]:
    vets = booking_repository.getAllVets(db)
    return [
        VetSlotResponse(
            veterinarianID=v.userID,
            name=v.name,
            specialisation=v.specialisation,
            availableSlots=v.availableSlots or [],
        )
        for v in vets
    ]


def setAvailability(db: Session, currentUser: User, slots: list[str]) -> list[str]:
    vet = booking_repository.getVetByUserId(db, currentUser.userID)
    vet.availableSlots = slots
    booking_repository.updateVet(db, vet)
    return slots


def makeBooking(db: Session, currentUser: User, body: BookingCreate) -> BookingResponse:
    vet = booking_repository.getVetById(db, body.veterinarianID)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    if body.timeslot not in (vet.availableSlots or []):
        raise HTTPException(status_code=409, detail="This timeslot is no longer available")

    if booking_repository.getConflicting(db, body.veterinarianID, body.timeslot):
        raise HTTPException(status_code=409, detail="This timeslot has already been booked")

    petId = None
    if body.petID:
        pet = pet_repository.getByIdAndOwner(db, body.petID, currentUser.userID)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        petId = pet.petID

    booking = Booking(
        createdAt=_now(),
        timeslot=body.timeslot,
        bookingStatus="pending",
        petOwnerID=currentUser.userID,
        veterinarianID=body.veterinarianID,
        petID=petId,
    )
    vet.availableSlots = [s for s in (vet.availableSlots or []) if s != body.timeslot]
    booking = booking_repository.add(db, booking)
    return _bookingPayload(booking)


def listBookings(db: Session, currentUser: User) -> list[BookingResponse]:
    if currentUser.role == "pet_owner":
        bookings = booking_repository.getByPetOwner(db, currentUser.userID)
    elif currentUser.role == "veterinarian":
        bookings = booking_repository.getByVet(db, currentUser.userID)
    else:
        raise HTTPException(
            status_code=403, detail="Only pet owners and vets can view bookings"
        )
    return [_bookingPayload(b) for b in bookings]


def acceptBooking(db: Session, bookingId: str, currentUser: User) -> BookingResponse:
    booking = booking_repository.getByIdAndVet(db, bookingId, currentUser.userID)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.bookingStatus != "pending":
        raise HTTPException(
            status_code=409, detail=f"Booking is already {booking.bookingStatus}"
        )
    booking.acceptBookingSlot()
    booking = booking_repository.update(db, booking)
    return _bookingPayload(booking)


def cancelBooking(db: Session, bookingId: str, currentUser: User) -> BookingResponse:
    booking = booking_repository.getById(db, bookingId)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if currentUser.userID not in (booking.petOwnerID, booking.veterinarianID):
        raise HTTPException(status_code=403, detail="Not authorised to cancel this booking")

    if booking.bookingStatus == "completed":
        raise HTTPException(status_code=409, detail="Cannot cancel a completed booking")

    previousStatus = booking.bookingStatus
    booking.cancelBooking()

    if previousStatus in ("pending", "accepted"):
        vet = booking_repository.getVetById(db, booking.veterinarianID)
        if vet:
            _restoreSlot(vet, booking.timeslot)

    booking = booking_repository.update(db, booking)
    return _bookingPayload(booking)
