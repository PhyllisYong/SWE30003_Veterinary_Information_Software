from difflib import SequenceMatcher
from typing import List, Optional
from sqlalchemy.orm import Session


def _fuzzy_score(query_tokens: list, text: str) -> float:
    """Score text against query tokens. Each token that fuzzy-matches a word in
    text (ratio >= 0.72) contributes its ratio to the total score."""
    text_words = [w.lower() for w in text.split() if len(w) > 2]
    if not text_words or not query_tokens:
        return 0.0
    score = 0.0
    for qt in query_tokens:
        best = max(
            (SequenceMatcher(None, qt, tw).ratio() for tw in text_words),
            default=0.0,
        )
        if best >= 0.72:
            score += best
    return score

from app.models.first_aid_content import FirstAidContent
from sqlalchemy.orm import with_polymorphic
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
        in-memory cache, including all concrete subclasses (Guide, Video, etc.).
        Called once at startup; call refreshCache() to reload after changes.
        """
        # Load the polymorphic hierarchy so that each row becomes its concrete subclass
        polymorphic = with_polymorphic(FirstAidContent, '*')
        self._contentRepository = (
            self._db.query(polymorphic)
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
        self,
        petType: Optional[str] = None,
        category: Optional[str] = None,
        contentType: Optional[str] = None,
         author_vet_id: Optional[str] = None,
        otherDesc: Optional[str] = None,
    ) -> List[FirstAidContent]:
        """
        Main search entry point — implements both alt paths from the sequence diagram:
          - accessFirstAidContent(petType, emergency): exact category match
          - accessFirstAidContent(petType, otherDesc): keyword search across
            title, emergencyCategory, and description when the user is unsure

        Args:
            petType:     e.g. "cat", "dog", "rabbit", "hamster", "guinea_pig"
            category:    exact match e.g. "bleeding", "choking", "fracture"
            contentType: e.g. "guide", "video"
            author_vet_id: e.g. "vet-123"
            otherDesc:   free-text description used when category is unknown

        Returns:
            List of matching FirstAidContent objects (Guide or Video instances).
        """
        results = self._contentRepository

        if petType:
            results = [c for c in results if c.petType.lower() == petType.lower()]

        if category:
            results = [
                c for c in results
                if c.emergencyCategory.lower() == category.lower()
            ]
        elif otherDesc:
            query_tokens = [w.lower() for w in otherDesc.split() if len(w) > 2]
            if query_tokens:
                scored = []
                for c in results:
                    score = max(
                        _fuzzy_score(query_tokens, c.title or ""),
                        _fuzzy_score(query_tokens, c.emergencyCategory or ""),
                        _fuzzy_score(query_tokens, c.description or ""),
                    )
                    if score > 0:
                        scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                results = [c for _, c in scored]

        if contentType:
            results = [
                c for c in results
                if c.content_type.lower() == contentType.lower()
            ]

        if author_vet_id:
            results = [
                c
                for c in results
                if c.authorVetID == author_vet_id
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
