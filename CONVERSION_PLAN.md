<!-- DO NOT OVERWRITE THIS FILE -->
<!-- This is the immutable conversion plan. Log results to CONVERSION_LOG.md instead. -->

# Ellen Blog - WordPress to Hugo Conversion Plan

## Overview

Convert ellen.harris-braun.com WordPress blog to Hugo static site with Ananke theme.

**Source:** `worldofthesickworldofthewell.wordpress.2025-12-31.xml`

**Theme:** Ananke (https://github.com/theNewDynamic/gohugo-theme-ananke)

**Key Requirements:**
- Use original banner: gc2.jpg
- No Giscus - historical comments only (embedded in posts)
- Preserve WordPress URL structure: `/YYYY/MM/DD/slug/`
- Dual subdomain support: ellen + ekhb (DNS/Cloudflare config)
- Custom CSS with Ellen's warm earth tones

## Content Conversion

- Parse WordPress XML export
- Convert posts, pages, and drafts to Hugo markdown
- Extract and embed historical comments in posts
- Download all media attachments
- Update image paths to `/images/filename`

## Configuration

- **hugo.toml**: Site config with permalink structure
- **params.toml**: Theme params with banner image
- **markup.toml**: Enable raw HTML for embedded comments
- **custom.css**: Ellen's color scheme (tan, sage green)

## Scripts

- `convert_wordpress.py` - Main XML to markdown conversion
- `extract_comments.py` - Comment embedding
- `download_media.py` - Media download with verification
- `verify_media.py` - Image integrity check

## Documentation Strategy

To prevent plan overwriting:
1. This file (CONVERSION_PLAN.md) - Immutable plan
2. CONVERSION_LOG.md - Append-only execution results
3. docs/MEDIA_REPORT.md - Media download/verification status

## Verification Checklist

- [ ] All posts converted
- [ ] All pages converted
- [ ] Comments embedded
- [ ] Media downloaded
- [ ] Banner configured
- [ ] URLs preserved
- [ ] Local build successful
- [ ] Deployment ready
