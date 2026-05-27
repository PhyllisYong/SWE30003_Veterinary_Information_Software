from pydantic import BaseModel
from typing import Optional

class PetCreate(BaseModel):
    petName: str
    petType: str   # "cat" | "dog" | "rabbit" | "hamster" | "guinea_pig"
    age: Optional[int] = None
    gender: Optional[str] = None  # "male" | "female"

class PetUpdate(BaseModel):
    petName: Optional[str] = None
    petType: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class PetResponse(BaseModel):
    petID: str
    petName: str
    petType: str
    age: Optional[int]
    gender: Optional[str]
    ownerID: str

    class Config:
        from_attributes = True