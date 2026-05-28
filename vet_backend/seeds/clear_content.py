"""
Delete all video rows from the database.

Run from vet_backend/:
    python -m seeds.clear_videos
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.guide import Guide
from app.models.video import Video


def clear() -> None:
    db = SessionLocal()
    try:
        items = db.query(Guide).all() + db.query(Video).all()
        if not items:
            print("No guide or video rows found.")
            return
        for item in items:
            print(f"  Deleting '{item.title}' ({item.contentID})")
            db.delete(item)
        db.commit()
        print(f"✓ Deleted {len(items)} item(s).")
    except Exception as e:
        db.rollback()
        print(f"✗ Failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clear()
