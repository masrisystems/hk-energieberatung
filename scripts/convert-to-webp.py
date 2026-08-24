"""
WebP Conversion Script for HK Energieberatung Google Business Profile & Website Assets.
Converts input images (PNG/JPG) to high-quality optimized WebP images,
ensuring strict compliance with filename conventions and image validation.
"""

import sys
import os
from pathlib import Path
from PIL import Image

def convert_to_webp(source_path: str, output_path: str, quality: int = 88, max_dimension: int = 1200) -> bool:
    source = Path(source_path)
    output = Path(output_path)

    if not source.exists():
        print(f"ERROR: Source file does not exist: {source_path}", file=sys.stderr)
        return False

    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(source) as img:
            # Convert RGBA to RGB if saving without alpha transparency or keep RGBA if needed
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            # Resize if dimensions exceed max_dimension while maintaining aspect ratio
            width, height = img.size
            if max(width, height) > max_dimension:
                scale = max_dimension / max(width, height)
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save as WebP
            img.save(output, "WEBP", quality=quality, method=6)

        # Verification
        if not output.exists() or output.stat().st_size == 0:
            print(f"ERROR: Output file failed to create: {output_path}", file=sys.stderr)
            return False

        with Image.open(output) as verified_img:
            if verified_img.format != "WEBP":
                print(f"ERROR: File format is not WEBP ({verified_img.format}): {output_path}", file=sys.stderr)
                return False
            print(f"SUCCESS: Converted {source.name} -> {output.name} ({verified_img.size[0]}x{verified_img.size[1]}, {output.stat().st_size / 1024:.1f} KB)")
            return True

    except Exception as e:
        print(f"EXCEPTION: Failed to convert {source_path} to WebP: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert-to-webp.py <source_path> <output_path> [quality] [max_dimension]")
        sys.exit(1)

    src = sys.argv[1]
    dest = sys.argv[2]
    q = int(sys.argv[3]) if len(sys.argv) > 3 else 88
    max_dim = int(sys.argv[4]) if len(sys.argv) > 4 else 1200

    success = convert_to_webp(src, dest, quality=q, max_dimension=max_dim)
    sys.exit(0 if success else 1)
