from sqlalchemy import Column, String, Integer, ForeignKey
from app.core.database import Base
from app.models.first_aid_content import FirstAidContent


class Video(FirstAidContent):
    """
    Concrete first-aid content type: a video with metadata.
    Actual streaming is delegated to the VideoHosting façade — this class
    only stores metadata (URL, duration).
    Inherits base publication lifecycle from FirstAidContent (Template Method).
    Stored in the `videos` table, joined to `first_aid_contents` via content_id.
    """

    __tablename__ = "videos"

    contentID = Column(
        "content_id",
        String,
        ForeignKey("first_aid_contents.content_id"),
        primary_key=True,
    )
    videoURL = Column("video_url", String, nullable=True)
    durationSec = Column("duration_sec", Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "video",
    }

    # ------------------------------------------------------------------
    # Template Method — required override
    # ------------------------------------------------------------------

    def display(self) -> dict:
        """
        Return the full video payload for the API, combining base metadata
        with video-specific fields.

        Note: this returns the stored videoURL for the frontend to pass to
        the VideoHosting façade. The controller (ContentController) is
        responsible for calling VideoHosting if a stream URL needs to be
        resolved — Video itself does not call VideoHosting directly here,
        keeping the domain class free of direct façade coupling at display
        time. If a streaming URL must be resolved server-side, do it in
        ContentController before returning the response.
        """
        data = self.getMetadata()
        data.update(
            {
                "videoURL": self.videoURL,
                "durationSec": self.durationSec,
            }
        )
        return data

    # ------------------------------------------------------------------
    # Video-specific methods
    # ------------------------------------------------------------------

    def getURL(self) -> str:
        """Return the stored video URL."""
        return self.videoURL

    def getDuration(self) -> int:
        """Return the video duration in seconds."""
        return self.durationSec

    def requestVideoStream(self) -> str | None:
        from app.services.video_hosting import video_hosting

        return video_hosting.displayVideo(self.videoURL)
