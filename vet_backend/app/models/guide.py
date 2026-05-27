from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from app.core.database import Base
from app.models.first_aid_content import FirstAidContent


class Guide(FirstAidContent):
    __tablename__ = "guides"

    contentID = Column("content_id", String, ForeignKey("first_aid_contents.content_id"), primary_key=True)
    steps = Column(JSON, nullable=True, default=list)
    # JSON list of strings e.g. ["Step 1: ...", "Step 2: ..."]
    stepCount = Column("step_count", Integer, nullable=True, default=0)

    __mapper_args__ = {
        "polymorphic_identity": "guide",
    }

    def getSteps(self) -> list:
        return self.steps or []

    def addStep(self, step: str) -> None:
        steps = list(self.steps or [])
        steps.append(step)
        self.steps = steps
        self.stepCount = len(steps)

    def updateStep(self, idx: int, txt: str) -> None:
        steps = list(self.steps or [])
        steps[idx] = txt
        self.steps = steps

    def removeStep(self, idx: int) -> None:
        steps = list(self.steps or [])
        steps.pop(idx)
        self.steps = steps
        self.stepCount = len(steps)
