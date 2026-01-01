#!/usr/bin/env python3
"""Convert WordPress XML export to Hugo markdown files."""

import xml.etree.ElementTree as ET
import os
import re
import html
from datetime import datetime
from pathlib import Path
import unicodedata

# Configuration
XML_PATH = '/home/eric/code/blogs/ellen/worldofthesickworldofthewell.wordpress.2025-12-31.xml'
POSTS_DIR = '/home/eric/code/blogs/ellen/blog-static/content/posts'
PAGES_DIR = '/home/eric/code/blogs/ellen/blog-static/content/pages'
DRAFTS_DIR = '/home/eric/code/blogs/ellen/blog-static/content/posts/_drafts'

# WordPress XML namespaces
namespaces = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
}

# Author mapping
AUTHOR_MAP = {
    'admin': 'Ellen Harris-Braun',
    'zippy314': 'Eric Harris-Braun',
    'spee': 'Spee Braun'
}

def clean_slug(slug):
    """Clean up slug for filename."""
    if not slug:
        return 'untitled'
    # Remove any problematic characters
    slug = re.sub(r'[^\w\-]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-').lower()

def html_to_markdown(content):
    """Convert HTML content to markdown-ish format.

    Note: We keep much of the HTML since Hugo's goldmark renderer
    handles it with unsafe=true. This preserves complex formatting.
    """
    if not content:
        return ''

    # Decode HTML entities
    content = html.unescape(content)

    # Fix WordPress image paths to use local images
    # Match various WordPress upload URL patterns
    content = re.sub(
        r'(src=["\'])https?://(?:ekhb|ellen)\.harris-braun\.com/blog/wp-content/uploads/\d{4}/\d{2}/([^"\']+)(["\'])',
        r'\1/images/\2\3',
        content
    )
    content = re.sub(
        r'(href=["\'])https?://(?:ekhb|ellen)\.harris-braun\.com/blog/wp-content/uploads/\d{4}/\d{2}/([^"\']+)(["\'])',
        r'\1/images/\2\3',
        content
    )

    # Convert common HTML to markdown where simple
    # Bold
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)

    # Italic
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)

    # Line breaks
    content = re.sub(r'<br\s*/?>', '\n', content)

    # Paragraphs - convert to double newlines
    content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)

    # Remove empty paragraphs
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Clean up WordPress caption shortcodes
    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'\1', content, flags=re.DOTALL)

    # Remove other WordPress shortcodes
    content = re.sub(r'\[[^\]]+\]', '', content)

    return content.strip()

def escape_yaml_string(s):
    """Escape a string for YAML front matter."""
    if not s:
        return '""'
    # If contains special chars, quote it
    if any(c in s for c in [':', '#', '"', "'", '\n', '[', ']', '{', '}']):
        # Escape double quotes and wrap in double quotes
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s

def parse_wordpress_xml(xml_path):
    """Parse WordPress XML and extract posts and pages."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    items = []

    for item in root.findall('.//item'):
        post_type_el = item.find('wp:post_type', namespaces)
        if post_type_el is None:
            continue
        post_type = post_type_el.text

        if post_type not in ['post', 'page']:
            continue

        # Extract basic fields
        title_el = item.find('title')
        title = title_el.text if title_el is not None and title_el.text else 'Untitled'

        post_name_el = item.find('wp:post_name', namespaces)
        slug = post_name_el.text if post_name_el is not None else None

        post_date_el = item.find('wp:post_date', namespaces)
        post_date = post_date_el.text if post_date_el is not None else None

        status_el = item.find('wp:status', namespaces)
        status = status_el.text if status_el is not None else 'publish'

        creator_el = item.find('dc:creator', namespaces)
        creator = creator_el.text if creator_el is not None else 'admin'
        author = AUTHOR_MAP.get(creator, creator)

        content_el = item.find('content:encoded', namespaces)
        content = content_el.text if content_el is not None else ''

        # Extract categories and tags
        categories = []
        tags = []
        for cat in item.findall('category'):
            domain = cat.get('domain')
            nicename = cat.get('nicename')
            if domain == 'category' and nicename:
                categories.append(nicename)
            elif domain == 'post_tag' and nicename:
                tags.append(nicename)

        # Get URL for pages (to preserve paths)
        link_el = item.find('link')
        link = link_el.text if link_el is not None else None

        items.append({
            'type': post_type,
            'title': title,
            'slug': slug,
            'date': post_date,
            'status': status,
            'author': author,
            'content': content,
            'categories': categories,
            'tags': tags,
            'link': link
        })

    return items

def create_front_matter(item):
    """Create Hugo front matter for an item."""
    lines = ['---']

    # Title
    lines.append(f'title: {escape_yaml_string(item["title"])}')

    # Date
    if item['date']:
        try:
            dt = datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
            lines.append(f'date: {dt.isoformat()}')
        except:
            lines.append(f'date: {item["date"]}')

    # Slug
    if item['slug']:
        lines.append(f'slug: "{clean_slug(item["slug"])}"')

    # Author
    lines.append(f'author: "{item["author"]}"')

    # Draft status
    if item['status'] != 'publish':
        lines.append('draft: true')

    # Categories
    if item['categories']:
        lines.append('categories:')
        for cat in item['categories']:
            lines.append(f'  - "{cat}"')

    # Tags
    if item['tags']:
        lines.append('tags:')
        for tag in item['tags']:
            lines.append(f'  - "{tag}"')

    lines.append('---')
    return '\n'.join(lines)

def write_item(item, output_dir):
    """Write an item to a markdown file."""
    if not item['date'] or not item['slug']:
        print(f"  Skipping item without date or slug: {item['title'][:50]}")
        return False

    # Parse date for filename
    try:
        dt = datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
        date_prefix = dt.strftime('%Y-%m-%d')
    except:
        print(f"  Skipping item with invalid date: {item['title'][:50]}")
        return False

    slug = clean_slug(item['slug'])
    filename = f"{date_prefix}-{slug}.md"
    filepath = os.path.join(output_dir, filename)

    # Create front matter and content
    front_matter = create_front_matter(item)
    content = html_to_markdown(item['content'])

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter)
        f.write('\n\n')
        f.write(content)
        f.write('\n')

    return True

def main():
    print("WordPress to Hugo Conversion")
    print("=" * 50)

    # Create output directories
    Path(POSTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(PAGES_DIR).mkdir(parents=True, exist_ok=True)
    Path(DRAFTS_DIR).mkdir(parents=True, exist_ok=True)

    # Parse WordPress XML
    print(f"\nParsing: {XML_PATH}")
    items = parse_wordpress_xml(XML_PATH)
    print(f"Found {len(items)} items (posts + pages)")

    # Separate by type and status
    posts = [i for i in items if i['type'] == 'post']
    pages = [i for i in items if i['type'] == 'page']

    published_posts = [p for p in posts if p['status'] == 'publish']
    draft_posts = [p for p in posts if p['status'] != 'publish']

    print(f"\nPosts: {len(published_posts)} published, {len(draft_posts)} drafts")
    print(f"Pages: {len(pages)}")

    # Convert posts
    print("\nConverting published posts...")
    converted_posts = 0
    for post in published_posts:
        if write_item(post, POSTS_DIR):
            converted_posts += 1
    print(f"  Converted: {converted_posts}")

    # Convert drafts
    print("\nConverting draft posts...")
    converted_drafts = 0
    for post in draft_posts:
        if write_item(post, DRAFTS_DIR):
            converted_drafts += 1
    print(f"  Converted: {converted_drafts}")

    # Convert pages
    print("\nConverting pages...")
    converted_pages = 0
    for page in pages:
        if write_item(page, PAGES_DIR):
            converted_pages += 1
    print(f"  Converted: {converted_pages}")

    print("\n" + "=" * 50)
    print("Conversion complete!")
    print(f"  Published posts: {converted_posts}")
    print(f"  Draft posts: {converted_drafts}")
    print(f"  Pages: {converted_pages}")

if __name__ == '__main__':
    main()
