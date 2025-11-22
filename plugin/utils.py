# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml  # YAML is used for its readability and consistency with MkDocs ecosystem
from bs4 import BeautifulSoup

WARNING = "WARNING (mkdocs_ultralytics_plugin):"
DEFAULT_AVATAR = requests.head("https://github.com/github.png", allow_redirects=True).url

# Shared, thread-safe cache to avoid duplicate API lookups and YAML thrash when running in parallel
_AUTHOR_CACHE: dict[str, dict[str, str | None]] | None = None
_CACHE_LOCK = threading.Lock()


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


def get_youtube_video_ids(soup: BeautifulSoup) -> list[str]:
    """Extract YouTube video IDs from iframe elements present in the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content from which YouTube video IDs need to be
            extracted.

    Returns:
        (List[str]): A list containing YouTube video IDs extracted from the HTML content.

    Examples:
        >>> from bs4 import BeautifulSoup
        >>> html_content = '''
        ... <html>
        ...     <body>
        ...         <iframe src="https://www.youtube.com/embed/example_id1"></iframe>
        ...         <iframe src="https://www.youtube.com/embed/example_id2"></iframe>
        ...     </body>
        ... </html>
        ... '''
        >>> soup = BeautifulSoup(html_content, 'html.parser')
        >>> video_ids = get_youtube_video_ids(soup)
        >>> print(video_ids)
        ['example_id1', 'example_id2']
    """
    youtube_ids = []
    iframes = soup.find_all("iframe", src=True)
    for iframe in iframes:
        if match := re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", iframe["src"]):
            youtube_ids.append(match[1])
    return youtube_ids


def get_github_username_from_email(
    email: str, cache: dict, file_path: str = "", verbose: bool = True
) -> tuple[str | None, str | None]:
    """Retrieve the GitHub username and avatar URL associated with the given email address.

    Args:
        email (str): The email address to retrieve the GitHub username for.
        cache (Dict): A dictionary containing cached email-GitHub username mappings.
        file_path (str, optional): Name of the file the user authored.
        verbose (bool, optional): Whether to print verbose output.

    Returns:
        username (str | None): GitHub username if found, None otherwise.
        avatar (str | None): Avatar URL if found, None otherwise.

    Notes:
        If the email ends with "@users.noreply.github.com", the function will parse the username directly from the
        email address. Uses the GitHub REST API to query the username if it's not found in the local cache. Ensure
        you comply with GitHub's rate limits and authentication requirements when querying their API.
    """
    # First, check if the email exists in the local cache file
    with _CACHE_LOCK:
        if email in cache:
            return cache[email].get("username"), cache[email].get("avatar")
    if not email.strip():
        if verbose:
            print(f"{WARNING} No author found for {file_path}")
        return None, None

    # If the email ends with "@users.noreply.github.com", parse the username directly
    if email.endswith("@users.noreply.github.com"):
        username = email.split("+")[-1].split("@")[0]
        avatar = f"https://github.com/{username}.png"
        with _CACHE_LOCK:
            cache[email] = {
                "username": username,
                "avatar": requests.head(avatar, allow_redirects=True).url,
            }
        return username, avatar

    # Fallback to GitHub REST API when not cached
    url = f"https://api.github.com/search/users?q={email}+in:email&sort=joined&order=asc"
    if verbose:
        print(f"Running GitHub REST API for author {email}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["total_count"] > 0:
            username = data["items"][0]["login"]
            avatar = data["items"][0]["avatar_url"]  # avatar_url key is correct here
            with _CACHE_LOCK:
                cache[email] = {
                    "username": username,
                    "avatar": requests.head(avatar, allow_redirects=True).url,
                }
            return username, avatar

    if verbose:
        print(f"{WARNING} No username found for {email}")
    with _CACHE_LOCK:
        cache[email] = {"username": None, "avatar": None}
    return None, None


def get_github_usernames_from_file(
    file_path: str,
    default_user: str | None = None,
    emails: dict[str, int] | None = None,
    repo_url: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Fetch GitHub usernames associated with a file using provided Git email counts.

    Args:
        file_path (str): The path to the file for which GitHub usernames are to be retrieved.
        default_user (str, optional): Default GitHub user email to use if no authors found.

    Returns:
        (Dict[str, Dict[str, any]]): A dictionary where keys are GitHub usernames or emails (if username is not
            found) and values are dictionaries containing:
            - 'email' (str): The email address of the author.
            - 'url' (str): The GitHub profile URL of the author.
            - 'changes' (int): The number of changes (commits) made by the author.
            - 'avatar' (str): The URL of the author's GitHub avatar.

    Examples:
        >>> print(get_github_usernames_from_file('mkdocs.yml', emails={'user@example.com': 2}))
        {'username1': {'email': 'user@example.com', 'url': 'https://github.com/username1', 'changes': 2, 'avatar': '...'}}
    """
    if emails is None:
        emails = {}
    else:
        emails = dict(emails)  # shallow copy to avoid mutating caller data

    # If no git info found but default_user provided, use default_user
    if not emails and default_user:
        emails[default_user] = 1

    # Load the local cache of GitHub usernames once per process (thread-safe)
    local_cache_file = Path("docs" if Path("docs").is_dir() else "") / "mkdocs_github_authors.yaml"
    global _AUTHOR_CACHE
    with _CACHE_LOCK:
        if _AUTHOR_CACHE is None:
            if local_cache_file.is_file():
                with local_cache_file.open("r") as f:
                    _AUTHOR_CACHE = yaml.safe_load(f) or {}
            else:
                _AUTHOR_CACHE = {}
        cache = _AUTHOR_CACHE

    github_repo_url = repo_url or "https://github.com/ultralytics/ultralytics"

    info = {}
    cache_updated = False
    for email, changes in emails.items():
        if not email and default_user:
            email = default_user
        was_cached = email in cache
        username, avatar = get_github_username_from_email(email, cache, file_path)
        # If we can't determine the user URL, revert to the GitHub file URL
        user_url = f"https://github.com/{username}" if username else github_repo_url
        info[username or email] = {
            "email": email,
            "url": user_url,
            "changes": changes,
            "avatar": avatar or DEFAULT_AVATAR,
        }
        cache_updated = cache_updated or (email in cache and not was_cached)

    # Save the local cache of GitHub usernames and avatar URLs if updated
    if cache_updated:
        with _CACHE_LOCK:
            _AUTHOR_CACHE = cache
            with local_cache_file.open("w") as f:
                yaml.safe_dump(cache, f)

    return info
