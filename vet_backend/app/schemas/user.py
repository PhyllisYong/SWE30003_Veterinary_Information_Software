from pydantic import BaseModel, EmailStr
from typing import Optional

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    contactNumber: Optional[str] = None