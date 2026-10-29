"""
Thumbnailer: Handles high-quality thumbnail generation and caching for SimageUI.
"""
import os
from PIL import Image

THUMB_SIZE = (256, 256)
THUMB_QUALITY = 90
THUMB_DIR = ".thumbnails"


def ensure_thumbnail(img_path: str, thumb_dir: str = THUMB_DIR) -> str:
    """
    Ensure a high-quality thumbnail exists for the given image.
    Returns the thumbnail path.
    """
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir, exist_ok=True)
    base = os.path.basename(img_path)
    thumb_path = os.path.join(thumb_dir, base)
    if os.path.exists(thumb_path):
        return thumb_path
    try:
        with Image.open(img_path) as im:
            im.thumbnail(THUMB_SIZE, Image.LANCZOS)
            im.save(thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True)
        return thumb_path
    except Exception:
        return ""
