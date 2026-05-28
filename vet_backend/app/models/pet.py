import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pet(Base):
    __tablename__ = "pets"

    petID = Column("pet_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    petName = Column("pet_name", String, nullable=False)
    petType = Column("pet_type", String, nullable=False)  # "cat" | "dog" | "rabbit" | "hamster" | "guinea_pig"
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # "male" | "female"
    ownerID = Column("owner_id", String, ForeignKey("pet_owners.user_id"), nullable=False)

    owner = relationship("PetOwner", back_populates="pets")

    def getPetInfo(self) -> dict:
        return {
            "petID": self.petID,
            "petName": self.petName,
            "petType": self.petType,
            "age": self.age,
            "gender": self.gender,
            "ownerID": self.ownerID,
        }

    def getOwnerID(self) -> str:
        return self.ownerID

    def getID(self) -> str:
        return self.petID

    def updatePetDetails(
        self,
        petName: str | None = None,
        petType: str | None = None,
        age: int | None = None,
        gender: str | None = None,
    ) -> None:
        if petName:
            self.petName = petName
        if petType:
            self.petType = petType
        if age is not None:
            self.age = age
        if gender:
            self.gender = gender
