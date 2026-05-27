from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from app.core.database import Base
from app.models.first_aid_content import FirstAidContent


class Guide(FirstAidContent):
    """
    Concrete first-aid content type: a step-by-step written procedure.
    Inherits base publication lifecycle from FirstAidContent (Template Method).
    Stored in the `guides` table, joined to `first_aid_contents` via content_id.
    """

    __tablename__ = "guides"

    contentID = Column(
        "content_id",
        String,
        ForeignKey("first_aid_contents.content_id"),
        primary_key=True,
    )
    steps = Column(JSON, nullable=True, default=list)
    # JSON list of strings e.g. ["Step 1: ...", "Step 2: ..."]
    stepCount = Column("step_count", Integer, nullable=True, default=0)

    __mapper_args__ = {
        "polymorphic_identity": "guide",
    }

    # ------------------------------------------------------------------
    # Template Method — required override
    # ------------------------------------------------------------------

    def display(self) -> dict:
        """
        Return the full guide payload for the API, combining base metadata
        with guide-specific step data.
        """
        data = self.getMetadata()
        data.update(
            {
                "steps": self.getSteps(),
                "stepCount": self.stepCount or 0,
            }
        )
        return data

    # ------------------------------------------------------------------
    # Guide-specific methods
    # ------------------------------------------------------------------

    def getSteps(self) -> list:
        """Return the list of step strings, or empty list if none set."""
        return self.steps or []

    def addStep(self, step: str) -> None:
        """Append a new step. Caller must persist via DatabaseManager."""
        steps = list(self.steps or [])
        steps.append(step)
        self.steps = steps
        self.stepCount = len(steps)

    def updateStep(self, idx: int, txt: str) -> None:
        """Replace the step at the given 0-based index."""
        steps = list(self.steps or [])
        if idx < 0 or idx >= len(steps):
            raise IndexError(f"Step index {idx} is out of range (guide has {len(steps)} steps).")
        steps[idx] = txt
        self.steps = steps

    def removeStep(self, idx: int) -> None:
        """Remove the step at the given 0-based index."""
        steps = list(self.steps or [])
        if idx < 0 or idx >= len(steps):
            raise IndexError(f"Step index {idx} is out of range (guide has {len(steps)} steps).")
        steps.pop(idx)
        self.steps = steps
        self.stepCount = len(steps)
