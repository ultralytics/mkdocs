# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license
"""Shared HTML processing logic for MkDocs plugin and postprocess script."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

from bs4 import BeautifulSoup

from plugin.utils import (
    calculate_time_difference,
    get_github_usernames_from_file,
    get_youtube_video_ids,
)

today = datetime.now()
DEFAULT_CREATION_DATE = (today - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S +0000")
DEFAULT_MODIFIED_DATE = (today - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S +0000")

COPY_ICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"/></svg>'
CHECK_ICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19L21 7l-1.41-1.41L9 16.17z"></path></svg>'


def get_git_info(file_path: str, add_authors: bool = True, default_author: str | None = None) -> dict[str, Any]:
    """Retrieve git information including creation/modified dates and optional authors."""
    file_path = str(Path(file_path).resolve())
    git_info = {
        "creation_date": DEFAULT_CREATION_DATE,
        "last_modified_date": DEFAULT_MODIFIED_DATE,
    }

    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL)
        creation_output = subprocess.check_output(
            ["git", "log", "--reverse", "--pretty=format:%ai", file_path]
        ).decode()
        creation_date = creation_output.split("\n")[0] if creation_output else ""
        last_modified_date = subprocess.check_output(["git", "log", "-1", "--pretty=format:%ai", file_path]).decode()
        git_info.update(
            {
                "creation_date": creation_date or DEFAULT_CREATION_DATE,
                "last_modified_date": last_modified_date or DEFAULT_MODIFIED_DATE,
            }
        )

        if add_authors:
            authors_info = get_github_usernames_from_file(file_path, default_user=default_author)
            git_info["authors"] = sorted(
                [(author, info["url"], info["changes"], info["avatar"]) for author, info in authors_info.items()],
                key=lambda x: x[2],
                reverse=True,
            )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return git_info


def parse_faq(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse FAQ questions and answers from HTML for JSON-LD structured data."""
    faqs = []
    if faq_section := soup.find("h2", string="FAQ"):
        current_section = faq_section.find_next_sibling()

        while current_section and current_section.name != "h2":
            if current_section.name == "h3":
                question = current_section.text.strip()
                answer = ""
                next_sibling = current_section.find_next_sibling()

                while next_sibling and next_sibling.name != "h3" and next_sibling.name != "h2":
                    if next_sibling.name == "p":
                        answer += f"{next_sibling.text.strip()} "
                    next_sibling = next_sibling.find_next_sibling()

                if question and answer:
                    faqs.append(
                        {
                            "@type": "Question",
                            "name": question,
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": answer.strip(),
                            },
                        }
                    )

            current_section = current_section.find_next_sibling()

    return faqs


def insert_content(soup: BeautifulSoup, content_to_insert) -> None:
    """Insert content before comments section or at end of main content."""
    if comments_header := soup.find("h2", id="__comments"):
        comments_header.insert_before(content_to_insert)
    elif md_typeset := soup.select_one(".md-content__inner"):
        md_typeset.append(content_to_insert)


def get_css() -> str:
    """CSS for git info, share buttons, and copy button."""
    return """
.md-content__button[onclick*="copyMarkdownForLLM"] svg {
    width: 1.2rem;
    height: 1.2rem;
    fill: currentColor;
}

.git-info, .dates-container, .authors-container, .share-buttons {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
}

.git-info {
    font-size: 0.8em;
    color: grey;
    margin-bottom: 10px;
}

.dates-container, .authors-container {
    margin-bottom: 10px;
}

.date-item, .author-link, .share-button {
    display: flex;
    align-items: center;
    cursor: pointer;
}

.date-item {
    margin-right: 10px;
}

.hover-item {
    transition: all 0.2s ease;
    filter: grayscale(100%);
}

.date-item .hover-item {
    font-size: 1.6em;
    margin-right: 5px;
}

.author-link .hover-item {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    margin-right: 3px;
    background-color: #f0f0f0;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

.author-link .hover-item[src] {
    opacity: 1;
}

.share-buttons {
    margin-top: 10px;
}

.share-button {
    background-color: #1da1f2;
    color: white;
    padding: 6px 12px;
    border-radius: 5px;
    border: none;
    font-size: 0.95em;
    margin: 5px;
    transition: all 0.2s ease;
}

.share-button.linkedin {
    background-color: #0077b5;
}

.share-button i {
    margin-right: 5px;
    font-size: 1.1em;
}

.share-button:hover,
.hover-item:hover {
    color: var(--md-accent-fg-color);
    transform: scale(1.1);
    filter: brightness(1.2) grayscale(0%);
}

@media (max-width: 1024px) {
    .git-info {
        flex-direction: column;
        align-items: flex-end;
    }
    .dates-container, .authors-container {
        width: 100%;
    }
}
"""


def process_html(
    html: str,
    page_url: str,
    title: str,
    src_path: str | None = None,
    default_image: str | None = None,
    default_author: str | None = None,
    keywords: str | None = None,
    add_desc: bool = True,
    add_image: bool = True,
    add_keywords: bool = True,
    add_share_buttons: bool = True,
    add_authors: bool = True,
    add_json_ld: bool = True,
    add_css: bool = True,
    add_copy_llm: bool = True,
) -> str:
    """Process HTML by adding metadata, git info, and social features."""
    soup = BeautifulSoup(html, "html.parser")

    # Ensure head and body exist
    if not soup.head:
        return html
    if not soup.body:
        soup.body = soup.new_tag("body")

    # Extract metadata from content
    meta = {}
    if add_desc and (
        first_paragraph := soup.find("article", class_="md-content__inner").find("p")
        if soup.find("article", class_="md-content__inner")
        else soup.find("p")
    ):
        desc = first_paragraph.text.strip()[:500]
        # Ensure description is not too short
        if len(desc) >= 10:
            meta["description"] = desc

    if add_image:
        if first_image := soup.find("img"):
            img_src = first_image.get("src", "")
            if img_src and (
                img_src.startswith(("http://", "https://", "/")) or not img_src.startswith(("javascript:", "data:"))
            ):
                meta["image"] = img_src
        elif youtube_ids := get_youtube_video_ids(soup):
            meta["image"] = f"https://img.youtube.com/vi/{youtube_ids[0]}/maxresdefault.jpg"
        elif default_image:
            meta["image"] = default_image

    # Add meta tags to head
    if not soup.find("meta", attrs={"name": "title"}):
        soup.head.append(soup.new_tag("meta", attrs={"name": "title", "content": title}))

    if add_share_buttons and not soup.find("link", rel="stylesheet", href=re.compile("font-awesome")):
        soup.head.append(
            soup.new_tag(
                "link",
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
            )
        )

    if add_keywords and keywords:
        if meta_keywords := soup.find("meta", attrs={"name": "keywords"}):
            meta_keywords["content"] = keywords
        else:
            soup.head.append(soup.new_tag("meta", attrs={"name": "keywords", "content": keywords}))

    if add_desc and "description" in meta:
        if meta_desc := soup.find("meta", attrs={"name": "description"}):
            meta_desc["content"] = meta["description"]
        else:
            soup.head.append(
                soup.new_tag(
                    "meta",
                    attrs={"name": "description", "content": meta["description"]},
                )
            )

    # Open Graph tags
    for prop, value in [
        ("og:type", "website"),
        ("og:url", page_url),
        ("og:title", title),
        ("og:description", meta.get("description", "")),
    ]:
        if tag := soup.find("meta", attrs={"property": prop}):
            tag["content"] = value
        else:
            soup.head.append(soup.new_tag("meta", attrs={"property": prop, "content": value}))

    if add_image and "image" in meta:
        if og_image := soup.find("meta", attrs={"property": "og:image"}):
            og_image["content"] = meta["image"]
        else:
            soup.head.append(soup.new_tag("meta", attrs={"property": "og:image", "content": meta["image"]}))

    # Twitter tags
    for prop, value in [
        ("twitter:card", "summary_large_image"),
        ("twitter:url", page_url),
        ("twitter:title", title),
        ("twitter:description", meta.get("description", "")),
    ]:
        if tag := soup.find("meta", attrs={"property": prop}):
            tag["content"] = value
        else:
            soup.head.append(soup.new_tag("meta", attrs={"property": prop, "content": value}))

    if add_image and "image" in meta and not soup.find("meta", attrs={"property": "twitter:image"}):
        soup.head.append(soup.new_tag("meta", attrs={"property": "twitter:image", "content": meta["image"]}))

    # Add Copy for LLM button
    if (
        add_copy_llm
        and "/reference/" not in page_url
        and (edit_btn := soup.find("a", {"title": "Edit this page"}))
        and not soup.find("a", onclick=re.compile("copyMarkdownForLLM"))
    ):
        copy_button = soup.new_tag(
            "a",
            href="javascript:void(0)",
            onclick="copyMarkdownForLLM(this); return false;",
            attrs={
                "class": "md-content__button md-icon",
                "title": "Copy page in Markdown format",
            },
        )
        copy_button.append(BeautifulSoup(COPY_ICON, "html.parser"))
        edit_btn.insert_after(copy_button)

        if not soup.find("script", string=re.compile(r"copyMarkdownForLLM")):
            script = soup.new_tag("script")
            script.string = f"""
            async function copyMarkdownForLLM(button) {{
                const editBtn = document.querySelector('a[title="Edit this page"]');
                if (!editBtn) return;

                const originalHTML = button.innerHTML;
                const checkIcon = '{CHECK_ICON}';

                let rawUrl = editBtn.href.replace('github.com', 'raw.githubusercontent.com');
                rawUrl = rawUrl.replace('/blob/', '/').replace('/tree/', '/');

                try {{
                    const response = await fetch(rawUrl);
                    let markdown = await response.text();

                    if (markdown.startsWith('---')) {{
                        const frontMatterEnd = markdown.indexOf('\\n---\\n', 3);
                        if (frontMatterEnd !== -1) {{
                            markdown = markdown.substring(frontMatterEnd + 5).trim();
                        }}
                    }}

                    const title = document.querySelector('h1')?.textContent || document.title;
                    const content = `# ${{title}}\\n\\nSource: ${{window.location.href}}\\n\\n---\\n\\n${{markdown}}`;

                    await navigator.clipboard.writeText(content);
                    button.innerHTML = checkIcon + ' Copied!';
                    setTimeout(() => {{ button.innerHTML = originalHTML; }}, 2000);
                }} catch (err) {{
                    button.innerHTML = '❌ Failed';
                    setTimeout(() => {{ button.innerHTML = originalHTML; }}, 2000);
                }}
            }}
            """
            soup.body.append(script)

    # Initialize git info with defaults
    git_info = {
        "creation_date": DEFAULT_CREATION_DATE,
        "last_modified_date": DEFAULT_MODIFIED_DATE,
    }

    # Add git information if source path available
    if src_path:
        git_info = get_git_info(src_path, add_authors=add_authors, default_author=default_author)

        # Only render git footer if we have real git history (not placeholder defaults)
        has_real_git_data = (
            git_info["creation_date"] != DEFAULT_CREATION_DATE
            or git_info["last_modified_date"] != DEFAULT_MODIFIED_DATE
            or "authors" in git_info
        )

        if add_authors and has_real_git_data:
            created_ago, created_date = calculate_time_difference(git_info["creation_date"])
            updated_ago, updated_date = calculate_time_difference(git_info["last_modified_date"])

            div = f"""<br><br>
<div class="git-info">
<div class="dates-container">
    <span class="date-item" title="This page was first created on {created_date}">
        <span class="hover-item">📅</span> Created {created_ago} ago
    </span>
    <span class="date-item" title="This page was last updated on {updated_date}">
        <span class="hover-item">✏️</span> Updated {updated_ago} ago
    </span>
</div>
<div class="authors-container">
"""

            if "authors" in git_info:
                for author in git_info["authors"]:
                    name, url, n, avatar = author
                    div += f"""<a href="{url}" class="author-link" title="{name} ({n} change{"s" * (n > 1)})">
    <img src="{avatar}{"&" if "?" in avatar else "?"}s=96" alt="{name}" class="hover-item" loading="lazy">
</a>
"""

            div += "</div></div>"

            if add_css and not soup.find("style", string=re.compile("git-info")):
                style_tag = soup.new_tag("style")
                style_tag.string = get_css()
                soup.head.append(style_tag)

            insert_content(soup, BeautifulSoup(div, "html.parser"))

    # Add JSON-LD structured data (always generated when enabled, uses defaults if no git info)
    if add_json_ld and not soup.find("script", type="application/ld+json"):
        ld_json_content = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "image": [meta["image"]] if "image" in meta else [],
            "datePublished": git_info["creation_date"],
            "dateModified": git_info["last_modified_date"],
            "author": [
                {
                    "@type": "Organization",
                    "name": "Ultralytics",
                    "url": "https://ultralytics.com/",
                }
            ],
            "abstract": meta.get("description", ""),
        }

        if faqs := parse_faq(soup):
            ld_json_content["@type"] = ["Article", "FAQPage"]
            ld_json_content["mainEntity"] = faqs

        ld_json_script = soup.new_tag("script", type="application/ld+json")
        ld_json_script.string = json.dumps(ld_json_content)
        soup.head.append(ld_json_script)

    # Add share buttons
    if add_share_buttons and not soup.find("div", class_="share-buttons"):
        encoded_url = quote(page_url, safe="")
        twitter_share_link = f"https://twitter.com/intent/tweet?url={encoded_url}"
        linkedin_share_link = f"https://www.linkedin.com/shareArticle?url={encoded_url}"

        share_buttons = f"""<div class="share-buttons">
    <button onclick="window.open('{twitter_share_link}', 'TwitterShare', 'width=550,height=680,menubar=no,toolbar=no'); return false;" class="share-button hover-item">
        <i class="fa-brands fa-x-twitter"></i> Tweet
    </button>
    <button onclick="window.open('{linkedin_share_link}', 'LinkedinShare', 'width=550,height=730,menubar=no,toolbar=no'); return false;" class="share-button hover-item linkedin">
        <i class="fa-brands fa-linkedin-in"></i> Share
    </button>
</div>
<br>
"""
        insert_content(soup, BeautifulSoup(share_buttons, "html.parser"))

    return str(soup)
