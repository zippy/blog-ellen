# Conversion Log

<!-- This file is append-only. Add new entries below, do not overwrite. -->

## 2025-12-31 - Initial Conversion

### Content Conversion Results

**Posts:**
- Published posts: 219 converted
- Draft posts: 2 converted (2 skipped - missing date/slug)
- Pages: 19 converted

**Comments:**
- Posts with comments: 157
- Total comments: 504
- Posts updated with comments: 152

### Media Download Results

- Total files: 300
- Successfully downloaded: 297
- Skipped (already exists): 3
- Failed: 0

### Image Verification Results

- Valid images: 286
- Corrupted: 0
- Zero-size: 0
- Non-image files (PDFs, audio, etc.): 11

### Files Created

```
blog-static/
├── config/_default/
│   ├── hugo.toml
│   ├── params.toml
│   └── markup.toml
├── content/
│   ├── posts/ (219 files)
│   ├── posts/_drafts/ (2 files)
│   └── pages/ (19 files)
├── scripts/
│   ├── convert_wordpress.py
│   ├── extract_comments.py
│   ├── download_media.py
│   └── verify_media.py
├── static/
│   ├── images/ (297 files)
│   └── css/custom.css
├── themes/ananke/ (git submodule)
├── docs/MEDIA_REPORT.md
├── CONVERSION_PLAN.md
└── CONVERSION_LOG.md (this file)
```

---

## 2025-12-31 - Theme Switch and Customization

### Theme Change
- Switched from Ananke to **Mainroad** theme for better sidebar support
- Added Mainroad as git submodule: `themes/mainroad/`

### Header Customization
- Added banner image (gc2.jpg) at top of page
- Created overlay tagline box with "WORLD OF THE SICK / WORLD OF THE WELL" and "breast cancer...again?"
- Navigation bar styled with sage green (#789993) background, centered items
- Removed logo section (title now in tagline overlay)

### Navigation Menu
- Home, 2013 & Onward, 2006-2007 Updates, Archives, Categories
- Added dropdown submenus for "2013 & Onward" and "2006-2007 Updates" matching sidebar links
- Custom `layouts/partials/menu.html` for dropdown support

### Sidebar Widgets (in order)
1. **Ellen Harris-Braun's Blog** - About widget with intro quote
2. **Links** - 16 external resource links (simple list, no categories)
3. **Background Info** - Two sections with clickable links:
   - 2013 & Onward (10 links to pages)
   - 2006-2007 Updates (7 links to pages)
4. **Categories** - Standard category list

### Post Display
- Homepage shows 5 most recent posts with "View all X posts" link
- Posts show "by FirstName" (Ellen, Eric, or Spee) in metadata
- Removed authorbox, author derived from post front matter
- Historical comments preserved in posts

### Custom CSS (`static/css/custom.css`)
- Banner and tagline overlay styling
- Sage green nav bar with dark blue text
- Dropdown menu styling
- Sidebar widget spacing (no bullets, tight spacing)
- Historical comments styling
- Color scheme from original site (#789993 sage, #1c346b dark blue, #566965 footer)

### Custom Layouts Created
- `layouts/partials/header.html` - Banner + tagline overlay
- `layouts/partials/menu.html` - Dropdown menu support
- `layouts/partials/authorbox.html` - Disabled (empty)
- `layouts/partials/post_meta/author.html` - Shows "by FirstName"
- `layouts/partials/widgets/about.html` - Ellen's intro quote
- `layouts/partials/widgets/background.html` - Section links
- `layouts/partials/widgets/links.html` - External resources
- `layouts/index.html` - Homepage with 5 posts + more link
- `layouts/_default/archives.html` - Posts grouped by year

### Configuration
- Hugo 0.146.0 (required for Mainroad compatibility)
- Highlight color changed from red to sage green (#789993)
- Permalinks: posts at `/YYYY/MM/DD/slug/`, pages at `/pages/slug/`

### Folder Renamed
- `blog-static` → `blog-ellen`

### Pending Tasks
1. Implement local search (Fuse.js) - deferred
2. Deploy to Cloudflare Pages
3. Configure DNS for ellen and ekhb subdomains
