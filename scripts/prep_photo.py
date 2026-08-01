"""
prep_photo.py

Turns a normal photo into a clean, high-contrast grayscale image that
converts nicely to ASCII. Run this once whenever you change your photo.

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(src_path: str, out_path: str = "source-prepped.png") -> None:
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Can't find {src_path}")

    # 1. Remove the background so only the subject remains (RGBA, transparent bg)
    with open(src, "rb") as f:
        cutout = remove(f.read())

    # 2. Composite onto pure white so the background maps to the blank
    #    end of the ASCII ramp (white -> spaces) instead of turning black.
    rgba = Image.open(__import__("io").BytesIO(cutout)).convert("RGBA")
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. Boost local contrast with CLAHE so a flatly-lit face gets real
    #    highlights and shadows instead of converting to a dark blob.
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
