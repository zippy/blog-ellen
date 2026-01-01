#!/usr/bin/env python3
"""Download all media attachments from WordPress export."""

import xml.etree.ElementTree as ET
import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

# Configuration
XML_PATH = '/home/eric/code/blogs/ellen/worldofthesickworldofthewell.wordpress.2025-12-31.xml'
OUTPUT_DIR = '/home/eric/code/blogs/ellen/blog-static/static/images'
REPORT_FILE = '/home/eric/code/blogs/ellen/blog-static/docs/MEDIA_REPORT.md'

# Additional files to download (banner, etc.)
EXTRA_FILES = [
    'https://ekhb.harris-braun.com/blog/wp-content/uploads/2015/05/gc2.jpg'
]

# WordPress XML namespaces
namespaces = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

def download_file(url, output_path, timeout=30):
    """Download a file from URL to output path.

    Returns: (success, error_message)
    """
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)

        if response.status_code == 404:
            # Try alternate domain
            if 'ekhb.harris-braun.com' in url:
                alt_url = url.replace('ekhb.harris-braun.com', 'ellen.harris-braun.com')
            else:
                alt_url = url.replace('ellen.harris-braun.com', 'ekhb.harris-braun.com')

            response = requests.get(alt_url, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)

            # Verify file is not empty
            if os.path.getsize(output_path) > 0:
                return True, None
            else:
                os.remove(output_path)
                return False, 'empty file'
        else:
            return False, f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return False, 'timeout'
    except requests.exceptions.ConnectionError:
        return False, 'connection error'
    except Exception as e:
        return False, str(e)

def download_media():
    """Download all media attachments with verification."""
    results = {
        'success': [],
        'failed': [],
        'skipped': [],
        'total': 0,
        'timestamp': datetime.now().isoformat()
    }

    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(REPORT_FILE)).mkdir(parents=True, exist_ok=True)

    # Collect all attachment URLs
    urls_to_download = []

    for item in root.findall('.//item'):
        post_type = item.find('wp:post_type', namespaces)
        if post_type is None or post_type.text != 'attachment':
            continue

        attachment_url = item.find('wp:attachment_url', namespaces)
        if attachment_url is None or not attachment_url.text:
            continue

        urls_to_download.append(attachment_url.text)

    # Add extra files
    urls_to_download.extend(EXTRA_FILES)

    results['total'] = len(urls_to_download)
    print(f"Found {results['total']} files to download")

    # Download each file
    for i, url in enumerate(urls_to_download):
        # Extract filename
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Progress indicator
        print(f"[{i+1}/{results['total']}] {filename}...", end=' ')

        # Skip if already exists
        if os.path.exists(output_path):
            results['skipped'].append({'url': url, 'file': filename, 'reason': 'exists'})
            print("skipped (exists)")
            continue

        # Download
        success, error = download_file(url, output_path)

        if success:
            size = os.path.getsize(output_path)
            results['success'].append({
                'url': url,
                'file': filename,
                'size': size
            })
            print(f"ok ({size} bytes)")
        else:
            results['failed'].append({
                'url': url,
                'file': filename,
                'reason': error
            })
            print(f"FAILED: {error}")

    # Write report
    write_report(results)
    return results

def write_report(results):
    """Generate MEDIA_REPORT.md with download results."""
    with open(REPORT_FILE, 'w') as f:
        f.write("# Media Download Report\n\n")
        f.write(f"Generated: {results['timestamp']}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total attachments: {results['total']}\n")
        f.write(f"- Successfully downloaded: {len(results['success'])}\n")
        f.write(f"- Skipped (already exists): {len(results['skipped'])}\n")
        f.write(f"- Failed: {len(results['failed'])}\n\n")

        if results['success']:
            total_size = sum(item['size'] for item in results['success'])
            f.write(f"Total downloaded: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)\n\n")

        if results['failed']:
            f.write("## Failed Downloads\n\n")
            for item in results['failed']:
                f.write(f"- **{item['file']}**: {item['reason']}\n")
                f.write(f"  - URL: `{item['url']}`\n")
            f.write("\n")

        if results['skipped']:
            f.write("## Skipped (Already Exists)\n\n")
            for item in results['skipped']:
                f.write(f"- {item['file']}\n")
            f.write("\n")

        f.write("## Next Steps\n\n")
        f.write("1. Review any failed downloads above\n")
        f.write("2. Run `python scripts/verify_media.py` to check image integrity\n")
        f.write("3. Manually download any critical missing files\n")

    print(f"\nReport written to: {REPORT_FILE}")

def main():
    print("Media Download")
    print("=" * 50)
    print(f"\nSource: {XML_PATH}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = download_media()

    print("\n" + "=" * 50)
    print("Download complete!")
    print(f"  Success: {len(results['success'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"  Failed: {len(results['failed'])}")

if __name__ == '__main__':
    main()
