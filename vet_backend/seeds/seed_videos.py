"""
Seed: two published first-aid videos.

Run from vet_backend/:
    python -m seeds.seed_videos
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import sessionLocal
from app.models.video import Video


VIDEOS = [
    dict(
        title="CPR for Dogs",
        description="Step-by-step guide to performing CPR on your dog in an emergency.",
        petType="dog",
        emergencyCategory="cpr",
        videoURL="https://www.youtube.com/embed/EG8bLRz5bVA",
        durationSec=None,
    ),
    dict(
        title="How to Bandage a Cat Wound",
        description="Learn how to safely apply a bandage to a wound on your cat.",
        petType="cat",
        emergencyCategory="wound",
        videoURL="https://www.youtube.com/embed/YikhHzJ2uUs",
        durationSec=None,
    ),
]


def seed() -> None:
    db = sessionLocal()
    try:
        for v in VIDEOS:
            video = Video(
                title=v["title"],
                description=v["description"],
                petType=v["petType"],
                emergencyCategory=v["emergencyCategory"],
                publicationStatus="published",
                videoURL=v["videoURL"],
                duration=v["durationSec"],
            )
            db.add(video)
            db.flush()
            print(f"[OK] Video seeded  '{v['title']}'  (id={video.contentID})")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
