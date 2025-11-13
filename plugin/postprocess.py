# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

"""Postprocess MkDocs/Zensical site by adding metadata, git info, and social features."""

from pathlib import Path

from plugin.processor import process_html


def process_html_file(
    html_path: Path,
    docs_dir: Path,
    site_url: str = "",
    default_image: str = None,
    default_author: str = None,
    add_desc: bool = True,
    add_image: bool = True,
    add_keywords: bool = True,
    add_share_buttons: bool = True,
    add_authors: bool = True,
    add_json_ld: bool = True,
    add_css: bool = True,
    add_copy_llm: bool = True,
    verbose: bool = False,
) -> None:
    """Process a single HTML file by delegating to shared processor."""
    from bs4 import BeautifulSoup

    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Get page URL
    rel_path = html_path.relative_to(html_path.parent.parent).as_posix()
    page_url = f"{site_url.rstrip('/')}/{rel_path}".replace("/index.html", "/")

    # Get title
    title = soup.find("h1").text if soup.find("h1") else soup.title.string if soup.title else ""

    # Find source markdown file
    src_path = None
    for md_file in docs_dir.rglob("*.md"):
        if md_file.stem == html_path.stem or (
            html_path.stem == "index" and md_file.parent.name == html_path.parent.name
        ):
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
    html_path.write_text(processed_html, encoding="utf-8")
    if verbose:
        print(f"Processed: {html_path.relative_to(html_path.parent.parent)}")


def postprocess_site(
    site_dir: str | Path = "site",
    docs_dir: str | Path = "docs",
    site_url: str = "",
    default_image: str = None,
    default_author: str = None,
    add_desc: bool = True,
    add_image: bool = True,
    add_keywords: bool = True,
    add_share_buttons: bool = True,
    add_authors: bool = True,
    add_json_ld: bool = True,
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
    print(f"Processing {len(html_files)} HTML files in {site_dir}")

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

    print(f"✅ Postprocessing complete: {len(html_files)} files processed")


if __name__ == "__main__":
    postprocess_site()
