# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

WARNING = "WARNING (mkdocs_ultralytics_plugin):"
TIMEOUT = 10  # seconds for network requests
DEFAULT_AVATAR_URL = "https://github.com/github.png"
_default_avatar_cache: str | None = None


def get_default_avatar() -> str:
    """Get the default avatar URL, lazily fetching the resolved URL on first call."""
    global _default_avatar_cache
    if _default_avatar_cache is None:
        try:
            _default_avatar_cache = requests.head(DEFAULT_AVATAR_URL, allow_redirects=True, timeout=TIMEOUT).url
        except Exception:
            _default_avatar_cache = DEFAULT_AVATAR_URL  # fallback to original URL
    return _default_avatar_cache


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


def _get_cache_file() -> Path:
    """Get the path to the GitHub author cache file."""
    return Path("docs" if Path("docs").is_dir() else "") / "mkdocs_github_authors.yaml"


def load_author_cache() -> dict[str, dict[str, str | None]]:
    """Load the GitHub author cache from disk."""
    cache_file = _get_cache_file()
    try:
        return yaml.safe_load(cache_file.read_text()) or {} if cache_file.is_file() else {}
    except Exception:
        return {}


def save_author_cache(cache: dict[str, dict[str, str | None]]) -> None:
    """Save the GitHub author cache to disk."""
    try:
        _get_cache_file().write_text(yaml.safe_dump(cache))
    except Exception as e:
        print(f"{WARNING} Failed to save author cache: {e}")


def _github_repo_path(repo_url: str | None) -> str | None:
    """Return the owner/repo path for a GitHub repository URL."""
    if not repo_url:
        return None
    parsed = urlparse(repo_url)
    if parsed.hostname != "github.com":
        return None
    path = parsed.path.strip("/")
    return path[:-4] if path.endswith(".git") else path or None


def resolve_github_user(
    email: str,
    cache: dict[str, dict[str, str | None]],
    repo_url: str | None = None,
    commit_sha: str | None = None,
    verbose: bool = True,
) -> dict[str, str | None]:
    """Resolve a single email to GitHub username and avatar, updating cache in-place.

    Args:
        email (str): The email address to resolve.
        cache (dict): The author cache dict (modified in-place if new entry added).
        repo_url (str, optional): GitHub repository URL used for commit API fallback.
        commit_sha (str, optional): Commit SHA authored by the email.
        verbose (bool): Whether to print API call info.

    Returns:
        dict with 'username' and 'avatar' keys (values may be None if not found).
    """
    if not email or not email.strip():
        return {"username": None, "avatar": None}

    # Return complete cached results immediately. Incomplete cached entries may be refreshed from commit metadata.
    if email in cache and cache[email].get("username") and cache[email].get("avatar"):
        return cache[email]

    # Parse username directly from GitHub noreply emails
    if email.endswith("@users.noreply.github.com"):
        username = email.split("+")[-1].split("@")[0]
        try:
            avatar = requests.head(f"https://github.com/{username}.png", allow_redirects=True, timeout=TIMEOUT).url
        except Exception:
            avatar = None
        cache[email] = {"username": username, "avatar": avatar}
        return cache[email]

    # Query the commit API when git history provides a commit for this email. This resolves authors whose commit email
    # is linked to a GitHub account but hidden from user search.
    if repo_path := _github_repo_path(repo_url):
        if commit_sha:
            try:
                response = requests.get(
                    f"https://api.github.com/repos/{repo_path}/commits/{commit_sha}", timeout=TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()
                    author = data.get("author") or {}
                    if author.get("login") and author.get("avatar_url"):
                        cache[email] = {"username": author["login"], "avatar": author["avatar_url"]}
                        return cache[email]
            except Exception:
                pass

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

    # Collect all unique emails across all files, with one representative commit SHA per email.
    all_emails: set[str] = set()
    commits: dict[str, str] = {}
    for entry in git_data.values():
        all_emails.update(entry.get("emails", {}).keys())
        for email, commit in entry.get("commits", {}).items():
            commits.setdefault(email, commit)
    if default_author:
        all_emails.add(default_author)
    all_emails.discard("")

    if not all_emails:
        return git_data

    # Load cache, resolve all emails, save cache (single disk write)
    cache = load_author_cache()
    cache_modified = False

    for email in sorted(all_emails):
        cached = cache.get(email, {})
        if email not in cache or (commits.get(email) and not (cached.get("username") and cached.get("avatar"))):
            resolve_github_user(email, cache, repo_url=repo_url, commit_sha=commits.get(email), verbose=verbose)
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
            email = email.strip() if email else ""
            if not email:
                email = default_author or ""
            if not email:
                continue
            info = cache.get(email, {"username": None, "avatar": None})
            username = info.get("username")
            avatar = info.get("avatar") or get_default_avatar()
            user_url = f"https://github.com/{username}" if username else github_repo_url
            authors.append((username or email, user_url, changes, avatar))

        # Sort by number of changes (descending)
        entry["authors"] = sorted(authors, key=lambda x: x[2], reverse=True)

    return git_data
