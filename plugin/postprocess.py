# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license
"""Postprocess MkDocs/Zensical site by adding metadata, git info, and social features."""

from __future__ import annotations

from pathlib import Path

from plugin.processor import process_html


def process_html_file(
    html_path: Path,
    docs_dir: Path,
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
) -> None:
    """Process a single HTML file by delegating to shared processor."""
    from bs4 import BeautifulSoup

    try:
        html = html_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError) as e:
        if verbose:
            print(f"Error reading {html_path}: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")

    # Get page URL
    rel_path = html_path.relative_to(html_path.parent.parent).as_posix()
    page_url = f"{site_url.rstrip('/')}/{rel_path}".replace("/index.html", "/")

    # Get title
    title = soup.find("h1").text if soup.find("h1") else soup.title.string if soup.title else ""

    # Find source markdown file
    src_path = None
    if docs_dir.exists():
        # Try exact stem match first
        for md_file in docs_dir.rglob("*.md"):
            if md_file.stem == html_path.stem:
                src_path = str(md_file)
                break

        # For index.html, try matching parent directory name
        if not src_path and html_path.stem == "index":
            for md_file in docs_dir.rglob("*.md"):
                if md_file.parent.name == html_path.parent.name or md_file.stem == "index":
                    src_path = str(md_file)
                    break

    # Process HTML
    processed_html = process_html(
        html=html,
        page_url=page_url,
        title=title,
        src_path=src_path,
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
    )

    # Write back
    try:
        html_path.write_text(processed_html, encoding="utf-8")
        if verbose:
            print(f"Processed: {html_path.relative_to(html_path.parent.parent)}")
    except (OSError, PermissionError) as e:
        if verbose:
            print(f"Error writing {html_path}: {e}")


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

    print(f"Processing {len(html_files)} HTML files in {site_dir}")

    processed = 0
    for html_file in html_files:
        process_html_file(
            html_file,
            docs_dir,
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
        processed += 1

    print(f"✅ Postprocessing complete: {processed}/{len(html_files)} files processed")


if __name__ == "__main__":
    postprocess_site()
