# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml

WARNING = "WARNING (mkdocs_ultralytics_plugin):"
TIMEOUT = 10  # seconds for network requests
DEFAULT_AVATAR = requests.head("https://github.com/github.png", allow_redirects=True, timeout=TIMEOUT).url


def calculate_time_difference(date_string: str) -> tuple[str, str]:
    """Calculate the time difference between a given date and the current date in a human-readable format.

    Args:
        date_string (str): Date and time string in the format "%Y-%m-%d %H:%M:%S %z".

    Returns:
        difference (str): Time difference in days, months, or years (e.g., "5 days", "2 months", "1 year").
        pretty_date (str): Given date formatted as "Month Day, Year" (e.g., "January 01, 2023").

    Examples:
        >>> calculate_time_difference("2023-01-01 00:00:00 +0000")
        ("5 months", "January 01, 2023")
    """
    date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
    pretty_date = date.strftime("%B %d, %Y")
    now = datetime.now(date.tzinfo)
    diff = now - date
    days = diff.days

    if days < 30:
        difference = f"{days} day{'s' if days != 1 else ''}"
    elif days < 365:
        months = days // 30
        difference = f"{months} month{'s' if months != 1 else ''}"
    else:
        years = days // 365
        difference = f"{years} year{'s' if years != 1 else ''}"
    return difference, pretty_date


def get_youtube_video_ids(soup) -> list[str]:
    """Extract YouTube video IDs from iframe elements present in the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content.

    Returns:
        (List[str]): A list containing YouTube video IDs extracted from the HTML content.
    """
    youtube_ids = []
    iframes = soup.find_all("iframe", src=True)
    for iframe in iframes:
        if match := re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", iframe["src"]):
            youtube_ids.append(match[1])
    return youtube_ids


def load_author_cache() -> dict[str, dict[str, str | None]]:
    """Load the GitHub author cache from disk."""
    cache_file = Path("docs" if Path("docs").is_dir() else "") / "mkdocs_github_authors.yaml"
    if cache_file.is_file():
        try:
            with cache_file.open("r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


def save_author_cache(cache: dict[str, dict[str, str | None]]) -> None:
    """Save the GitHub author cache to disk."""
    cache_file = Path("docs" if Path("docs").is_dir() else "") / "mkdocs_github_authors.yaml"
    try:
        with cache_file.open("w") as f:
            yaml.safe_dump(cache, f)
    except Exception as e:
        print(f"{WARNING} Failed to save author cache: {e}")


def resolve_github_user(
    email: str, cache: dict[str, dict[str, str | None]], verbose: bool = True
) -> dict[str, str | None]:
    """Resolve a single email to GitHub username and avatar, updating cache in-place.

    Args:
        email (str): The email address to resolve.
        cache (dict): The author cache dict (modified in-place if new entry added).
        verbose (bool): Whether to print API call info.

    Returns:
        dict with 'username' and 'avatar' keys (values may be None if not found).
    """
    if not email or not email.strip():
        return {"username": None, "avatar": None}

    # Return cached result if available
    if email in cache:
        return cache[email]

    # Parse username directly from GitHub noreply emails
    if email.endswith("@users.noreply.github.com"):
        username = email.split("+")[-1].split("@")[0]
        avatar = requests.head(f"https://github.com/{username}.png", allow_redirects=True, timeout=TIMEOUT).url
        cache[email] = {"username": username, "avatar": avatar}
        return cache[email]

    # Query GitHub REST API
    if verbose:
        print(f"Running GitHub REST API for author {email}")
    try:
        response = requests.get(
            f"https://api.github.com/search/users?q={email}+in:email&sort=joined&order=asc", timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("total_count", 0) > 0:
                username = data["items"][0]["login"]
                avatar = requests.head(data["items"][0]["avatar_url"], allow_redirects=True, timeout=TIMEOUT).url
                cache[email] = {"username": username, "avatar": avatar}
                return cache[email]
    except Exception:
        pass

    if verbose:
        print(f"{WARNING} No username found for {email}")
    cache[email] = {"username": None, "avatar": None}
    return cache[email]


def resolve_all_authors(
    git_data: dict[str, dict[str, Any]],
    default_author: str | None = None,
    repo_url: str | None = None,
    verbose: bool = True,
) -> dict[str, dict[str, Any]]:
    """Pre-resolve all unique emails from git_data to GitHub usernames.

    This should be called ONCE in the main process before spawning workers. It collects all unique emails, resolves
    them, saves the cache, and returns git_data with 'authors' pre-populated for each file.

    Args:
        git_data (dict): The git metadata dict from build_git_map().
        default_author (str, optional): Default author email if no git info.
        repo_url (str, optional): Repository URL for fallback links.
        verbose (bool): Whether to print progress info.

    Returns:
        dict: Updated git_data with 'authors' list added to each entry.
    """
    if not git_data:
        return git_data

    # Collect all unique emails across all files
    all_emails: set[str] = set()
    for entry in git_data.values():
        all_emails.update(entry.get("emails", {}).keys())
    if default_author:
        all_emails.add(default_author)
    all_emails.discard("")

    if not all_emails:
        return git_data

    # Load cache, resolve all emails, save cache (single disk write)
    cache = load_author_cache()
    cache_modified = False

    for email in sorted(all_emails):
        if email not in cache:
            resolve_github_user(email, cache, verbose=verbose)
            cache_modified = True

    if cache_modified:
        save_author_cache(cache)

    # Build authors list for each file entry
    github_repo_url = repo_url or "https://github.com/ultralytics/ultralytics"

    for file_path, entry in git_data.items():
        emails = entry.get("emails", {})
        if not emails and default_author:
            emails = {default_author: 1}

        authors = []
        for email, changes in emails.items():
            # Skip empty emails, use default_author if available
            if not email or not email.strip():
                if default_author:
                    email = default_author
                else:
                    continue
            info = cache.get(email, {"username": None, "avatar": None})
            username = info.get("username")
            avatar = info.get("avatar") or DEFAULT_AVATAR
            user_url = f"https://github.com/{username}" if username else github_repo_url
            authors.append((username or email, user_url, changes, avatar))

        # Sort by number of changes (descending)
        entry["authors"] = sorted(authors, key=lambda x: x[2], reverse=True)

    return git_data
