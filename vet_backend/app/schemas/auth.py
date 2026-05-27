from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str                              # "pet_owner" | "veterinarian" | "association_admin"
    contactNumber: Optional[str] = None   # PetOwner only
    licenseNumber: Optional[str] = None   # Veterinarian only
    specialisation: Optional[str] = None  # Veterinarian only
    workID: Optional[str] = None          # AssociationAdministrator only


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    status: str
    token: str
    userID: str
    name: str
    role: str
