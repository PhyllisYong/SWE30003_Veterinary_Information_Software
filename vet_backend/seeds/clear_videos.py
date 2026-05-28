"""
Delete all video rows from the database.

Run from vet_backend/:
    python -m seeds.clear_videos
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.video import Video
from app.models.first_aid_content import FirstAidContent


def clear() -> None:
    db = SessionLocal()
    try:
        videos = db.query(Video).all()
        if not videos:
            print("No video rows found.")
            return
        for v in videos:
            print(f"  Deleting '{v.title}' ({v.contentID})")
            db.delete(v)
        db.commit()
        print(f"✓ Deleted {len(videos)} video(s).")
    except Exception as e:
        db.rollback()
        print(f"✗ Failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clear()
