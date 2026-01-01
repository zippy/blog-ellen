#!/usr/bin/env python3
"""Verify downloaded images can be opened and rendered."""

import os
from pathlib import Path

# Configuration
IMAGE_DIR = '/home/eric/code/blogs/ellen/blog-static/static/images'
REPORT_FILE = '/home/eric/code/blogs/ellen/blog-static/docs/MEDIA_REPORT.md'

# Try to import PIL, but don't fail if not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not installed. Will do basic file checks only.")
    print("Install with: pip install Pillow")

def verify_images():
    """Check each image file can be opened."""
    results = {
        'valid': [],
        'corrupted': [],
        'non_image': [],
        'zero_size': []
    }

    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory not found: {IMAGE_DIR}")
        return results

    files = os.listdir(IMAGE_DIR)
    print(f"Found {len(files)} files to verify")

    for filename in sorted(files):
        filepath = os.path.join(IMAGE_DIR, filename)
        ext = Path(filename).suffix.lower()

        # Check for zero-size files
        if os.path.getsize(filepath) == 0:
            results['zero_size'].append(filename)
            print(f"  {filename}: ZERO SIZE")
            continue

        # Non-image files
        if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']:
            results['non_image'].append(filename)
            continue

        # Image files
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            if PIL_AVAILABLE:
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                    results['valid'].append(filename)
                except Exception as e:
                    results['corrupted'].append({'file': filename, 'error': str(e)})
                    print(f"  {filename}: CORRUPTED - {e}")
            else:
                # Basic check: file exists and has content
                results['valid'].append(filename)
        else:
            # Unknown extension, treat as non-image
            results['non_image'].append(filename)

    return results

def append_to_report(results):
    """Append verification results to the media report."""
    with open(REPORT_FILE, 'a') as f:
        f.write("\n---\n\n")
        f.write("## Image Verification Results\n\n")
        f.write(f"- Valid images: {len(results['valid'])}\n")
        f.write(f"- Corrupted images: {len(results['corrupted'])}\n")
        f.write(f"- Zero-size files: {len(results['zero_size'])}\n")
        f.write(f"- Non-image files (PDFs, etc.): {len(results['non_image'])}\n\n")

        if results['corrupted']:
            f.write("### Corrupted Files\n\n")
            for item in results['corrupted']:
                f.write(f"- **{item['file']}**: {item['error']}\n")
            f.write("\n")

        if results['zero_size']:
            f.write("### Zero-Size Files\n\n")
            for filename in results['zero_size']:
                f.write(f"- {filename}\n")
            f.write("\n")

        if results['non_image']:
            f.write("### Non-Image Files\n\n")
            for filename in results['non_image']:
                f.write(f"- {filename}\n")
            f.write("\n")

    print(f"\nResults appended to: {REPORT_FILE}")

def main():
    print("Image Verification")
    print("=" * 50)
    print(f"\nDirectory: {IMAGE_DIR}")
    print()

    results = verify_images()

    print("\n" + "=" * 50)
    print("Verification complete!")
    print(f"  Valid images: {len(results['valid'])}")
    print(f"  Corrupted: {len(results['corrupted'])}")
    print(f"  Zero-size: {len(results['zero_size'])}")
    print(f"  Non-image: {len(results['non_image'])}")

    # Append to report if it exists
    if os.path.exists(REPORT_FILE):
        append_to_report(results)
    else:
        print(f"\nNote: Report file not found, skipping append: {REPORT_FILE}")

    # Return exit code based on corrupted/zero-size files
    if results['corrupted'] or results['zero_size']:
        return 1
    return 0

if __name__ == '__main__':
    exit(main())
