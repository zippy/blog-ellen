#!/usr/bin/env python3
"""Fix WordPress thumbnail image paths in Hugo markdown files.

WordPress generates multiple sizes like image-150x150.jpg, image-300x200.jpg.
We only have the originals, so strip the size suffixes.
"""

import os
import re

CONTENT_DIR = '/home/eric/code/blogs/ellen/blog-static/content'

# Pattern to match WordPress thumbnail suffixes
# Matches: filename-150x150.jpg, filename-300x200.png, etc.
THUMBNAIL_PATTERN = re.compile(r'(/images/[^"\'>\s]+?)-\d+x\d+(\.(jpg|jpeg|png|gif))', re.IGNORECASE)

def fix_file(filepath):
    """Fix image paths in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all matches
    matches = THUMBNAIL_PATTERN.findall(content)
    if not matches:
        return 0

    # Replace thumbnail paths with original paths
    new_content = THUMBNAIL_PATTERN.sub(r'\1\2', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return len(matches)

    return 0

def main():
    total_fixed = 0
    files_fixed = 0

    for root, dirs, files in os.walk(CONTENT_DIR):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)
            fixed = fix_file(filepath)

            if fixed > 0:
                print(f"Fixed {fixed} image paths in {filename}")
                total_fixed += fixed
                files_fixed += 1

    print(f"\nTotal: Fixed {total_fixed} image paths in {files_fixed} files")

if __name__ == '__main__':
    main()
