from pydantic import BaseModel


class BookingCreate(BaseModel):
    vetID: str
    timeslot: str  # ISO 8601 datetime string e.g. "2025-06-01T09:00:00Z"
    petID: str | None = None


class BookingResponse(BaseModel):
    bookingID: str
    createdAt: str
    timeslot: str
    bookingStatus: str
    petOwnerID: str
    vetID: str
    petID: str | None = None
    petName: str | None = None
    petType: str | None = None

    model_config = {"from_attributes": True}


class VetSlotResponse(BaseModel):
    vetID: str
    name: str
    specialisation: str | None
    availableSlots: list[str]

    model_config = {"from_attributes": True}
