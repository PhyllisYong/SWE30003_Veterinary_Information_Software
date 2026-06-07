import re
from typing import Optional

_YT_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
]


class VideoHostingFacade:
    """
    Facade for YouTube video hosting.
    Handles URL parsing, embed URL generation, and thumbnail resolution.
    No API key required.
    """

    def extractVideoID(self, videoURL: str) -> Optional[str]:
        """Return the 11-char YouTube video ID from any supported URL format, or None."""
        for pattern in _YT_PATTERNS:
            match = re.search(pattern, videoURL)
            if match:
                return match.group(1)
        return None

    def isValidYouTubeURL(self, videoURL: str) -> bool:
        """Return True if videoURL is a recognised YouTube video URL."""
        return self.extractVideoID(videoURL) is not None

    def getEmbedURL(self, videoURL: str) -> Optional[str]:
        """Convert any YouTube URL to its embed form, or None if not a YouTube URL."""
        videoId = self.extractVideoID(videoURL)
        if not videoId:
            return None
        return f"https://www.youtube.com/embed/{videoId}"

    def displayVideo(self, videoURL: str) -> Optional[str]:
        """Resolve a playable video stream URL."""
        return self.getEmbedURL(videoURL)

    def getThumbnailURL(self, videoURL: str, quality: str = "hqdefault") -> Optional[str]:
        """
        Return a YouTube thumbnail URL without an API call.
        quality options: default, mqdefault, hqdefault, sddefault, maxresdefault
        """
        videoId = self.extractVideoID(videoURL)
        if not videoId:
            return None
        return f"https://img.youtube.com/vi/{videoId}/{quality}.jpg"


# Module-level singleton — import and use directly.
video_hosting = VideoHostingFacade()
