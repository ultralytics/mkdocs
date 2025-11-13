# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license
"""Postprocess MkDocs/Zensical site by adding metadata, git info, and social features."""

from __future__ import annotations

from pathlib import Path

from plugin.processor import process_html


def process_html_file(
    html_path: Path,
    site_dir: Path,
    md_index: dict[str, str],
    site_url: str = "",
    default_image: str | None = None,
    default_author: str | None = None,
    add_desc: bool = True,
    add_image: bool = True,
    add_keywords: bool = True,
    add_share_buttons: bool = True,
    add_authors: bool = False,
    add_json_ld: bool = False,
    add_css: bool = True,
    add_copy_llm: bool = True,
    verbose: bool = False,
) -> bool:
    """Process a single HTML file by delegating to shared processor.

    Returns:
        bool: True if file was successfully processed and written, False otherwise.
    """
    from bs4 import BeautifulSoup

    try:
        html = html_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError) as e:
        if verbose:
            print(f"Error reading {html_path}: {e}")
        return False

    soup = BeautifulSoup(html, "html.parser")

    # Get page URL - calculate relative path from site_dir
    rel_path = html_path.relative_to(site_dir).as_posix()
    page_url = f"{site_url.rstrip('/')}/{rel_path}".replace("/index.html", "/")

    # Get title
    title = soup.find("h1").text if soup.find("h1") else soup.title.string if soup.title else ""

    # Extract keywords from existing meta tag if present
    keywords = None
    if meta_keywords := soup.find("meta", attrs={"name": "keywords"}):
        keywords = meta_keywords.get("content")

    # Find source markdown file from prebuilt index using relative path
    html_rel = html_path.relative_to(site_dir).with_suffix("").as_posix()
    if html_rel.endswith("/index"):
        html_rel = html_rel[:-6]  # Remove /index suffix
    src_path = md_index.get(html_rel or "index") or md_index.get(f"{html_rel}/index")

    # Process HTML
    processed_html = process_html(
        html=html,
        page_url=page_url,
        title=title,
        src_path=src_path,
        default_image=default_image,
        default_author=default_author,
        keywords=keywords,
        add_desc=add_desc,
        add_image=add_image,
        add_keywords=add_keywords,
        add_share_buttons=add_share_buttons,
        add_authors=add_authors,
        add_json_ld=add_json_ld,
        add_css=add_css,
        add_copy_llm=add_copy_llm,
    )

    # Write back
    try:
        html_path.write_text(processed_html, encoding="utf-8")
        if verbose:
            print(f"Processed: {html_path.relative_to(site_dir)}")
        return True
    except (OSError, PermissionError) as e:
        if verbose:
            print(f"Error writing {html_path}: {e}")
        return False


def postprocess_site(
    site_dir: str | Path = "site",
    docs_dir: str | Path = "docs",
    site_url: str = "",
    default_image: str | None = None,
    default_author: str | None = None,
    add_desc: bool = True,
    add_image: bool = True,
    add_keywords: bool = True,
    add_share_buttons: bool = True,
    add_authors: bool = False,
    add_json_ld: bool = False,
    add_css: bool = True,
    add_copy_llm: bool = True,
    verbose: bool = True,
) -> None:
    """Process all HTML files in the site directory."""
    site_dir = Path(site_dir)
    docs_dir = Path(docs_dir)

    if not site_dir.exists():
        print(f"Site directory not found: {site_dir}")
        return

    html_files = list(site_dir.rglob("*.html"))
    if not html_files:
        print(f"No HTML files found in {site_dir}")
        return

    # Build markdown index once (O(N) instead of O(N²)) using relative paths as keys
    md_index = {}
    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            rel_path = md_file.relative_to(docs_dir).with_suffix("").as_posix()
            md_index[rel_path] = str(md_file)

    print(f"Processing {len(html_files)} HTML files in {site_dir}")

    processed = 0
    for html_file in html_files:
        success = process_html_file(
            html_file,
            site_dir,
            md_index,
            site_url=site_url,
            default_image=default_image,
            default_author=default_author,
            add_desc=add_desc,
            add_image=add_image,
            add_keywords=add_keywords,
            add_share_buttons=add_share_buttons,
            add_authors=add_authors,
            add_json_ld=add_json_ld,
            add_css=add_css,
            add_copy_llm=add_copy_llm,
            verbose=verbose,
        )
        if success:
            processed += 1

    print(f"✅ Postprocessing complete: {processed}/{len(html_files)} files processed")


if __name__ == "__main__":
    postprocess_site()
