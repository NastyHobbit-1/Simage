"""
ImageScanner: Scans a directory for images and manages thumbnail generation.
"""
import os
from typing import List
from thumbnailer import ensure_thumbnail, THUMB_DIR

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

def scan_images(folder: str) -> List[str]:
    """
    Return a list of image file paths in the given folder.
    """
    files = []
    for f in os.listdir(folder):
        ext = os.path.splitext(f)[1].lower()
        if ext in IMG_EXTS:
            files.append(os.path.join(folder, f))
    return files

def ensure_thumbnails_for_folder(folder: str) -> List[str]:
    """
    Ensure thumbnails for all images in the folder. Returns list of thumbnail paths.
    """
    images = scan_images(folder)
    thumb_dir = os.path.join(folder, THUMB_DIR)
    thumbs = [ensure_thumbnail(img, thumb_dir) for img in images]
    return thumbs
