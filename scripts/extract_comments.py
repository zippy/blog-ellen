#!/usr/bin/env python3
"""Extract comments from WordPress XML and add them to Hugo markdown files."""

import xml.etree.ElementTree as ET
import os
import re
import html
from datetime import datetime

# Configuration
XML_PATH = '/home/eric/code/blogs/ellen/worldofthesickworldofthewell.wordpress.2025-12-31.xml'
CONTENT_DIR = '/home/eric/code/blogs/ellen/blog-static/content'

# WordPress XML namespaces
namespaces = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

def parse_wordpress_xml(xml_path):
    """Parse WordPress XML and extract posts with their comments."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    posts_with_comments = {}

    for item in root.findall('.//item'):
        post_type = item.find('wp:post_type', namespaces)
        if post_type is None:
            continue
        post_type_text = post_type.text

        if post_type_text not in ['post', 'page']:
            continue

        post_name = item.find('wp:post_name', namespaces)
        post_date = item.find('wp:post_date', namespaces)
        post_status = item.find('wp:status', namespaces)

        if post_name is None or post_date is None:
            continue

        if post_status is not None and post_status.text != 'publish':
            continue

        slug = post_name.text
        date_str = post_date.text

        # Parse date
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            date_prefix = dt.strftime('%Y-%m-%d')
        except:
            continue

        # Find comments for this post
        comments = []
        for comment in item.findall('wp:comment', namespaces):
            comment_approved = comment.find('wp:comment_approved', namespaces)
            if comment_approved is None or comment_approved.text != '1':
                continue

            comment_type = comment.find('wp:comment_type', namespaces)
            if comment_type is not None and comment_type.text in ['pingback', 'trackback']:
                continue

            author = comment.find('wp:comment_author', namespaces)
            author_url = comment.find('wp:comment_author_url', namespaces)
            date = comment.find('wp:comment_date', namespaces)
            content = comment.find('wp:comment_content', namespaces)

            if author is None or content is None:
                continue

            author_text = author.text or 'Anonymous'
            author_url_text = author_url.text if author_url is not None and author_url.text and author_url.text != 'http://' else None
            date_text = date.text if date is not None else ''
            content_text = content.text or ''

            # Clean up content
            content_text = html.unescape(content_text)

            comments.append({
                'author': author_text,
                'author_url': author_url_text,
                'date': date_text,
                'content': content_text
            })

        if comments:
            # Sort comments by date
            comments.sort(key=lambda x: x['date'])
            posts_with_comments[f"{date_prefix}-{slug}"] = comments

    return posts_with_comments

def format_comments_html(comments):
    """Format comments as HTML for embedding in markdown.

    Uses simple CSS classes that match our custom.css styling.
    """
    if not comments:
        return ""

    html_parts = ['<div class="historical-comments">']
    html_parts.append('<h2>Historical Comments</h2>')

    for comment in comments:
        author = html.escape(comment['author'])
        date = comment['date']
        content = comment['content']
        author_url = comment.get('author_url')

        # Format date nicely
        try:
            dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            date_formatted = dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            date_formatted = date

        html_parts.append('<div class="comment">')
        html_parts.append('<div class="comment-meta">')

        if author_url:
            html_parts.append(f'<a href="{html.escape(author_url)}" class="comment-author">{author}</a>')
        else:
            html_parts.append(f'<span class="comment-author">{author}</span>')

        html_parts.append(f' &mdash; {html.escape(date_formatted)}')
        html_parts.append('</div>')

        # Process content - convert newlines to <br> and preserve some formatting
        content_html = html.escape(content)
        content_html = content_html.replace('\n\n', '</p><p>')
        content_html = content_html.replace('\n', '<br>')
        content_html = f'<p>{content_html}</p>'

        html_parts.append(f'<div class="comment-content">{content_html}</div>')
        html_parts.append('</div>')

    html_parts.append('</div>')

    return '\n'.join(html_parts)

def add_comments_to_posts(posts_with_comments, content_dir):
    """Add historical comments to Hugo markdown files."""
    posts_dir = os.path.join(content_dir, 'posts')

    updated = 0
    for filename in os.listdir(posts_dir):
        if not filename.endswith('.md'):
            continue

        # Skip index files
        if filename == '_index.md':
            continue

        # Extract the key (date-slug) from filename
        # Filename format: 2005-01-27-blogging.md
        match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', filename)
        if not match:
            continue

        key = f"{match.group(1)}-{match.group(2)}"

        if key not in posts_with_comments:
            continue

        comments = posts_with_comments[key]
        comments_html = format_comments_html(comments)

        filepath = os.path.join(posts_dir, filename)

        # Read existing content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if comments already added
        if 'historical-comments' in content:
            continue

        # Append comments to the end
        content = content.rstrip() + '\n\n' + comments_html + '\n'

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Added {len(comments)} comments to {filename}")
        updated += 1

    return updated

def main():
    print("Comment Extraction")
    print("=" * 50)

    print(f"\nParsing: {XML_PATH}")
    posts_with_comments = parse_wordpress_xml(XML_PATH)
    print(f"Found {len(posts_with_comments)} posts with comments")

    total_comments = sum(len(c) for c in posts_with_comments.values())
    print(f"Total comments: {total_comments}")

    print("\nAdding comments to Hugo posts...")
    updated = add_comments_to_posts(posts_with_comments, CONTENT_DIR)
    print(f"\nUpdated {updated} posts with historical comments")

if __name__ == '__main__':
    main()
