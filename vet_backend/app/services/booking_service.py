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


def _booking_payload(booking: Booking) -> BookingResponse:
    return BookingResponse(
        bookingID=booking.bookingID,
        createdAt=booking.createdAt,
        timeslot=booking.timeslot,
        bookingStatus=booking.bookingStatus,
        petOwnerID=booking.petOwnerID,
        vetID=booking.vetID,
        petID=booking.petID,
        petName=booking.pet.petName if booking.pet else None,
        petType=booking.pet.petType if booking.pet else None,
    )


def _restore_slot(vet: Veterinarian, timeslot: str) -> None:
    slots = list(vet.availableSlots or [])
    if timeslot not in slots:
        slots.append(timeslot)
        slots.sort()
        vet.availableSlots = slots


def list_vets(db: Session) -> list[VetSlotResponse]:
    vets = booking_repository.get_all_vets(db)
    return [
        VetSlotResponse(
            vetID=v.userID,
            name=v.name,
            specialisation=v.specialisation,
            availableSlots=v.availableSlots or [],
        )
        for v in vets
    ]


def set_availability(db: Session, current_user: User, slots: list[str]) -> list[str]:
    vet = booking_repository.get_vet_by_user_id(db, current_user.userID)
    vet.availableSlots = slots
    booking_repository.update_vet(db, vet)
    return slots


def make_booking(db: Session, current_user: User, body: BookingCreate) -> BookingResponse:
    vet = booking_repository.get_vet_by_id(db, body.vetID)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    if body.timeslot not in (vet.availableSlots or []):
        raise HTTPException(status_code=409, detail="This timeslot is no longer available")

    if booking_repository.get_conflicting(db, body.vetID, body.timeslot):
        raise HTTPException(status_code=409, detail="This timeslot has already been booked")

    pet_id = None
    if body.petID:
        pet = pet_repository.get_by_id_and_owner(db, body.petID, current_user.userID)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        pet_id = pet.petID

    booking = Booking(
        createdAt=_now(),
        timeslot=body.timeslot,
        bookingStatus="pending",
        petOwnerID=current_user.userID,
        vetID=body.vetID,
        petID=pet_id,
    )
    vet.availableSlots = [s for s in (vet.availableSlots or []) if s != body.timeslot]
    booking = booking_repository.add(db, booking)
    return _booking_payload(booking)


def list_bookings(db: Session, current_user: User) -> list[BookingResponse]:
    if current_user.role == "pet_owner":
        bookings = booking_repository.get_by_pet_owner(db, current_user.userID)
    elif current_user.role == "veterinarian":
        bookings = booking_repository.get_by_vet(db, current_user.userID)
    else:
        raise HTTPException(
            status_code=403, detail="Only pet owners and vets can view bookings"
        )
    return [_booking_payload(b) for b in bookings]


def accept_booking(db: Session, booking_id: str, current_user: User) -> BookingResponse:
    booking = booking_repository.get_by_id_and_vet(db, booking_id, current_user.userID)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.bookingStatus != "pending":
        raise HTTPException(
            status_code=409, detail=f"Booking is already {booking.bookingStatus}"
        )
    booking.acceptBookingSlot()
    booking = booking_repository.update(db, booking)
    return _booking_payload(booking)


def cancel_booking(db: Session, booking_id: str, current_user: User) -> BookingResponse:
    booking = booking_repository.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.userID not in (booking.petOwnerID, booking.vetID):
        raise HTTPException(status_code=403, detail="Not authorised to cancel this booking")

    if booking.bookingStatus == "completed":
        raise HTTPException(status_code=409, detail="Cannot cancel a completed booking")

    previous_status = booking.bookingStatus
    booking.cancelBooking()

    if previous_status in ("pending", "accepted"):
        vet = booking_repository.get_vet_by_id(db, booking.vetID)
        if vet:
            _restore_slot(vet, booking.timeslot)

    booking = booking_repository.update(db, booking)
    return _booking_payload(booking)
