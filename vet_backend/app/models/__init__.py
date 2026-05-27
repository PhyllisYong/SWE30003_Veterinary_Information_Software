# Import all models here so Alembic autogenerate detects every table.
# Order matters: parents before children (FK dependencies).

from app.models.user import User
from app.models.pet_owner import PetOwner
from app.models.veterinarian import Veterinarian
from app.models.association_admin import AssociationAdministrator
from app.models.pet import Pet
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.video import Video
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.chat import VeterinaryAdviceChat
from app.models.message import Message
from app.models.booking import Booking
from app.models.quiz_result import QuizResult

__all__ = [
    "User",
    "PetOwner",
    "Veterinarian",
    "AssociationAdministrator",
    "Pet",
    "FirstAidContent",
    "Guide",
    "Video",
    "Quiz",
    "Question",
    "Answer",
    "VeterinaryAdviceChat",
    "Message",
    "Booking",
    "QuizResult",
]
