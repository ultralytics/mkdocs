# Ultralytics MkDocs plugin 🚀, AGPL-3.0 license

import contextlib
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
import yaml  # install this with `pip install PyYAML` if not installed yet
from bs4 import BeautifulSoup

WARNING = "WARNING (mkdocs_ultralytics_plugin):"


def calculate_time_difference(date_string):
    """
    Calculate the time difference between a given date and the current date in a human-readable format.

    Args:
        date_string (str): Date and time string in the format "%Y-%m-%d %H:%M:%S %z".

    Returns:
        str: Time difference in days, months, or years (e.g., "5 days", "2 months", "1 year").


    Example:
        >>> calculate_time_difference("2023-01-01 00:00:00 +0000")
        "5 months"
    """
    date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
    now = datetime.now(date.tzinfo)
    diff = now - date
    days = diff.days

    if days < 30:
        return f"{days} day{'s' if days != 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"


def get_youtube_video_ids(soup: BeautifulSoup) -> list:
    """
    Extract YouTube video IDs from iframe elements present in the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML content from which YouTube video IDs need to be extracted.

    Returns:
        list: A list containing YouTube video IDs in string format extracted from the HTML content.

    Examples:
        ```
        from bs4 import BeautifulSoup

        # Sample HTML content with YouTube iframes
        html_content = '''
        <html>
            <body>
                <iframe src="https://www.youtube.com/embed/example_id1"></iframe>
                <iframe src="https://www.youtube.com/embed/example_id2"></iframe>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        video_ids = get_youtube_video_ids(soup)
        print(video_ids)  # Output: ['example_id1', 'example_id2']
        ```
    """
    youtube_ids = []
    iframes = soup.find_all("iframe", src=True)
    for iframe in iframes:
        if match := re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", iframe["src"]):
            youtube_ids.append(match[1])
    return youtube_ids


def get_github_username_from_email(email, local_cache, file_path="", verbose=True):
    """
    Retrieves the GitHub username associated with the given email address.

    Args:
        email (str): The email address to retrieve the GitHub username for.
        local_cache (dict): A dictionary containing cached email-GitHub username mappings.
        file_path (str, optional): Name of the file the user authored. Defaults to ''.
        verbose (bool, optional): Whether to print verbose output. Defaults to True.

    Returns:
        (str | None): The GitHub username associated with the email address, or None if not found.

    Note:
        If the email ends with "@users.noreply.github.com", the function will parse the username directly from the email address.
        Uses the GitHub REST API to query the username if it's not found in the local cache. Ensure you comply with GitHub's rate
        limits and authentication requirements when querying their API.
    """

    # First, check if the email exists in the local cache file
    if email in local_cache:
        return local_cache[email]
    elif not email.strip():
        if verbose:
            print(f"{WARNING} No author found for {file_path}")
        return None

    # If the email ends with "@users.noreply.github.com", parse the username directly
    if email.endswith("@users.noreply.github.com"):
        username = email.split("+")[-1].split("@")[0]
        local_cache[email] = username  # save the username in the local cache for future use
        return username

    # If the email is not found in the cache, query GitHub REST API
    url = f"https://api.github.com/search/users?q={email}+in:email&sort=joined&order=asc"
    if verbose:
        print(f"Running GitHub REST API for author {email}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["total_count"] > 0:
            username = data["items"][0]["login"]
            local_cache[email] = username  # save the username in the local cache for future use
            return username

    if verbose:
        print(f"{WARNING} No username found for {email}")
    local_cache[email] = None  # save the username in the local cache for future use
    return None  # couldn't find username


def get_github_usernames_from_file(file_path):
    """
    Fetch GitHub usernames associated with a file using Git Log and Git Blame commands.

    Args:
        file_path (str): The path to the file for which GitHub usernames are to be retrieved.

    Returns:
        (dict): A dictionary where keys are GitHub usernames or emails (if username is not found) and values are dictionaries containing:
            - 'email' (str): The email address of the author.
            - 'url' (str): The GitHub profile URL of the author.
            - 'changes' (int): The number of changes (commits) made by the author.

    Examples:
        ```python
        print(get_github_usernames_from_file('mkdocs.yml'))
        ```
    """
    # Fetch author emails using 'git log'
    authors_emails_log = (
        subprocess.check_output(["git", "log", "--pretty=format:%ae", Path(file_path).resolve()])
        .decode("utf-8")
        .split("\n")
    )
    emails = dict(Counter(authors_emails_log))

    # Fetch author emails using 'git blame'
    with contextlib.suppress(Exception):
        authors_emails_blame = (
            subprocess.check_output(
                ["git", "blame", "--line-porcelain", Path(file_path).resolve()], stderr=subprocess.DEVNULL
            )
            .decode("utf-8")
            .split("\n")
        )
        authors_emails_blame = [line.split(" ")[1] for line in authors_emails_blame if line.startswith("author-mail")]
        authors_emails_blame = [email.strip("<>") for email in authors_emails_blame]
        emails_blame = dict(Counter(authors_emails_blame))

        # Merge the two email lists, adding any missing authors from 'git blame' as a 1-commit change
        for email in emails_blame:
            if email not in emails:
                emails[email] = 1  # Only add new authors from 'git blame' with a 1-commit change

    # Load the local cache of GitHub usernames
    local_cache_file = Path("docs" if Path("docs").is_dir() else "") / "mkdocs_github_authors.yaml"
    if local_cache_file.is_file():
        with local_cache_file.open("r") as f:
            local_cache = yaml.safe_load(f) or {}
    else:
        local_cache = {}

    github_repo_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf-8").strip()
    if github_repo_url.endswith(".git"):
        github_repo_url = github_repo_url[:-4]
    if github_repo_url.startswith("git@"):
        github_repo_url = "https://" + github_repo_url[4:].replace(":", "/")

    info = {}
    for k, v in emails.items():
        username = get_github_username_from_email(k, local_cache, file_path)
        # If we can't determine the user URL, revert to the GitHub file URL
        user_url = f"https://github.com/{username}" if username else github_repo_url
        info[username or k] = {"email": k, "url": user_url, "changes": v}

    # Save the local cache of GitHub usernames
    with local_cache_file.open("w") as f:
        yaml.safe_dump(local_cache, f)

    return info
