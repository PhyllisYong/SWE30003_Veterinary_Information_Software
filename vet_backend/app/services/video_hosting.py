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

    def extractVideoId(self, url: str) -> Optional[str]:
        """Return the 11-char YouTube video ID from any supported URL format, or None."""
        for pattern in _YT_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def isValidYouTubeUrl(self, url: str) -> bool:
        """Return True if url is a recognised YouTube video URL."""
        return self.extractVideoId(url) is not None

    def getEmbedUrl(self, url: str) -> Optional[str]:
        """Convert any YouTube URL to its embed form, or None if not a YouTube URL."""
        video_id = self.extractVideoId(url)
        if not video_id:
            return None
        return f"https://www.youtube.com/embed/{video_id}"

    def displayVideo(self, url: str) -> Optional[str]:
        """Design-named facade method for resolving a playable video stream URL."""
        return self.getEmbedUrl(url)

    def getThumbnailUrl(self, url: str, quality: str = "hqdefault") -> Optional[str]:
        """
        Return a YouTube thumbnail URL without an API call.
        quality options: default, mqdefault, hqdefault, sddefault, maxresdefault
        """
        video_id = self.extractVideoId(url)
        if not video_id:
            return None
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


# Module-level singleton — import and use directly.
video_hosting = VideoHostingFacade()
