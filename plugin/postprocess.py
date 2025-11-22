# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license
"""Postprocess MkDocs/Zensical site by adding metadata, git info, and social features."""

from __future__ import annotations

import os
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

try:
    from ultralytics.utils import TQDM  # progress bars
except ImportError:
    TQDM = None

import plugin.processor as processor
from plugin.processor import process_html

# Shared worker state for process pools (avoids re-pickling large read-only data per task)
_WORKER_STATE: dict[str, Any] | None = None


def _set_worker_state(state: dict[str, Any]) -> None:
    global _WORKER_STATE
    _WORKER_STATE = state


def _process_file(html_file: Path) -> bool:
    if _WORKER_STATE is None:
        raise RuntimeError("Worker state not initialized")
    return process_html_file(
        html_file,
        _WORKER_STATE["site_dir"],
        _WORKER_STATE["md_index"],
        _WORKER_STATE["git_data"],
        _WORKER_STATE["repo_url"],
        site_url=_WORKER_STATE["site_url"],
        default_image=_WORKER_STATE["default_image"],
        default_author=_WORKER_STATE["default_author"],
        add_desc=_WORKER_STATE["add_desc"],
        add_image=_WORKER_STATE["add_image"],
        add_keywords=_WORKER_STATE["add_keywords"],
        add_share_buttons=_WORKER_STATE["add_share_buttons"],
        add_authors=_WORKER_STATE["add_authors"],
        add_json_ld=_WORKER_STATE["add_json_ld"],
        add_css=_WORKER_STATE["add_css"],
        add_copy_llm=_WORKER_STATE["add_copy_llm"],
        verbose=_WORKER_STATE["verbose"],
        log=None,
    )


def process_html_file(
    html_path: Path,
    site_dir: Path,
    md_index: dict[str, str],
    git_data: dict[str, dict[str, str | dict]] | None,
    repo_url: str | None,
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
    log: Callable[[str], None] | None = print,
) -> bool:
    """Process a single HTML file by delegating to shared processor.

    Returns:
        bool: True if file was successfully processed and written, False otherwise.
    """
    from bs4 import BeautifulSoup

    try:
        html = html_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError) as e:
        if verbose and log:
            log(f"Error reading {html_path}: {e}")
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
        git_data=git_data,
        repo_url=repo_url,
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
        return True
    except (OSError, PermissionError) as e:
        if verbose and log:
            log(f"Error writing {html_path}: {e}")
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
    use_processes: bool = True,
    workers: int | None = None,
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

    worker_count = min(os.cpu_count() or 1, workers or os.cpu_count() or 1)

    # Build markdown index once (O(N) instead of O(N²)) using relative paths as keys
    md_index = {md.relative_to(docs_dir).with_suffix("").as_posix(): str(md) for md in docs_dir.rglob("*.md")} if docs_dir.exists() else {}

    mode = "process" if use_processes else "thread"
    print(f"Processing {len(html_files)} HTML files in {site_dir} with {worker_count} {mode} worker(s)")

    processed = 0
    repo_url = None
    git_data = None
    if (add_authors or add_json_ld) and md_index:
        repo_url, git_data = processor.build_git_map(list(md_index.values()))

    progress = TQDM(total=len(html_files), desc="Postprocessing", unit="file", disable=not verbose) if TQDM else None
    # Enable logging only for the synchronous path; pools run without per-task log_fn to remain pickle-safe.
    log_fn = (progress.write if verbose and progress else print if verbose else None) if worker_count == 1 else None

    task_kwargs = dict(
        site_dir=site_dir,
        md_index=md_index,
        git_data=git_data,
        repo_url=repo_url,
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

    if worker_count == 1:
        for html_file in html_files:
            success = process_html_file(html_file, **task_kwargs, log=log_fn)
            processed += bool(success)
            if progress:
                progress.update(1)
    else:
        if use_processes:
            state = {**task_kwargs}
            executor_context = ProcessPoolExecutor(
                max_workers=worker_count, initializer=_set_worker_state, initargs=(state,)
            )
            submit_fn = lambda ex, f: ex.submit(_process_file, f)
        else:
            executor_context = ThreadPoolExecutor(max_workers=worker_count)
            submit_fn = lambda ex, f: ex.submit(process_html_file, f, **task_kwargs, log=log_fn)

        with executor_context as executor:
            future_to_file = {submit_fn(executor, html_file): html_file for html_file in html_files}

            for future in as_completed(future_to_file):
                html_file = future_to_file[future]
                try:
                    success = future.result()
                except Exception as e:
                    success = False
                    if verbose:
                        (log_fn or print)(f"Error processing {html_file}: {e}")
                if success:
                    processed += 1
                if progress:
                    progress.update(1)

    if progress:
        progress.close()

    print(f"✅ Postprocessing complete: {processed}/{len(html_files)} files processed")


if __name__ == "__main__":
    postprocess_site()
