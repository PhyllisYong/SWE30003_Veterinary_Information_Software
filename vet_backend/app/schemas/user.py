from pydantic import BaseModel, EmailStr
from typing import Optional


class UserResponse(BaseModel):
    userID: str
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    contactNumber: Optional[str] = None