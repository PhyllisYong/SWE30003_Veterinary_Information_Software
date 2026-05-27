from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.video import Video


class SearchEngine:
    """
    Service class that filters and retrieves FirstAidContent items.
    Holds an in-memory content repository loaded from the database at startup.

    Bootstrap order (from HANDOVER.md §8):
        Step 2 — load FirstAidContent hierarchy from DB
        Step 3 — instantiate SearchEngine (this class), which calls loadRepository()

    Usage:
        engine = SearchEngine(db_session)
        results = engine.searchContent(petType="cat", category="bleeding")
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._contentRepository: List[FirstAidContent] = []
        self.loadRepository()

    # ------------------------------------------------------------------
    # Repository management
    # ------------------------------------------------------------------

    def loadRepository(self) -> None:
        """
        Load all published FirstAidContent rows from the database into the
        in-memory cache. Only published content is surfaced to end users.
        Called once at startup; call refreshCache() to reload after changes.
        """
        self._contentRepository = (
            self._db.query(FirstAidContent)
            .filter(FirstAidContent.publicationStatus == "published")
            .all()
        )

    def refreshCache(self) -> None:
        """
        Reload the in-memory repository from the database.
        Call this after any content is published, unpublished, or deleted
        so that search results stay current without a server restart.
        """
        self.loadRepository()

    # ------------------------------------------------------------------
    # Search and filter
    # ------------------------------------------------------------------

    def searchContent(
        self, petType: Optional[str] = None, category: Optional[str] = None
    ) -> List[FirstAidContent]:
        """
        Main search entry point. Filters the repository by petType and/or
        emergencyCategory. Either or both may be None (returns all if both omitted).

        Args:
            petType:  e.g. "cat", "dog", "rabbit", "hamster", "guinea_pig"
            category: e.g. "bleeding", "choking", "fracture"

        Returns:
            List of matching FirstAidContent objects (Guide or Video instances).
        """
        results = self._contentRepository

        if petType:
            results = [c for c in results if c.petType.lower() == petType.lower()]

        if category:
            results = [
                c
                for c in results
                if c.emergencyCategory.lower() == category.lower()
            ]

        return results

    def filterByPetType(self, petType: str) -> List[FirstAidContent]:
        """Return all published content for the given pet type."""
        return [
            c
            for c in self._contentRepository
            if c.petType.lower() == petType.lower()
        ]

    def filterByCategory(self, category: str) -> List[FirstAidContent]:
        """Return all published content for the given emergency category."""
        return [
            c
            for c in self._contentRepository
            if c.emergencyCategory.lower() == category.lower()
        ]

    def getContentByID(self, contentID: str) -> Optional[FirstAidContent]:
        """
        Look up a single content item by ID from the in-memory cache.
        Returns None if not found (e.g. unpublished content won't be in cache).
        If you need to fetch unpublished content (e.g. admin view), query the
        DB directly via DatabaseManager instead of using this method.
        """
        for item in self._contentRepository:
            if item.contentID == contentID:
                return item
        return None
