import subprocess
from collections import Counter
from pathlib import Path

import requests
import yaml  # install this with `pip install PyYAML` if not installed yet


def get_github_username_from_email(email, local_cache, verbose=True):
    # First, check if the email exists in the local cache file
    if email in local_cache:
        return local_cache[email]

    # If the email ends with "@users.noreply.github.com", parse the username directly
    if email.endswith("@users.noreply.github.com"):
        username = email.split("+")[1].split("@")[0]
        local_cache[email] = username  # save the username in the local cache for future use
        return username

    # If the email is not found in the cache, query GitHub REST API
    url = f"https://api.github.com/search/users?q={email}+in:email&sort=joined&order=asc"
    if verbose:
        print(f'Running GitHub REST API for author {email}')
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] > 0:
            username = data['items'][0]['login']
            local_cache[email] = username  # save the username in the local cache for future use
            return username

    if verbose:
        print(f'WARNING: No username found for {email}')
    local_cache[email] = None  # save the username in the local cache for future use
    return None  # couldn't find username


def get_github_usernames_from_file(file_path):
    authors_emails = subprocess.check_output(['git', 'log', '--pretty=format:%ae', Path(file_path).resolve()]).decode(
        'utf-8').split('\n')
    emails = dict(Counter(authors_emails))  # dict of {author: changes}

    # Load the local cache of GitHub usernames
    local_cache_file = Path('docs' if Path('docs').is_dir() else '') / 'mkdocs_github_authors.yaml'
    if local_cache_file.is_file():
        with local_cache_file.open('r') as f:
            local_cache = yaml.safe_load(f) or {}
    else:
        local_cache = {}

    github_repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode('utf-8').strip()
    if github_repo_url.endswith(".git"):
        github_repo_url = github_repo_url[:-4]
    if github_repo_url.startswith("git@"):
        github_repo_url = "https://" + github_repo_url[4:].replace(":", "/")

    file_url = f"{github_repo_url}/blob/main/{get_relative_path_to_git_root(file_path)}"
    info = {}
    for k, v in emails.items():
        username = get_github_username_from_email(k, local_cache)
        # if we can't determine the user URL, revert to the GitHub file URL
        user_url = f'https://github.com/{username}' if username else file_url
        info[username or k] = {'email': k, 'url': user_url, 'changes': v}

    # Save the local cache of GitHub usernames
    with local_cache_file.open('w') as f:
        yaml.safe_dump(local_cache, f)

    return info


def get_relative_path_to_git_root(file_path):
    # Get the Git root directory
    git_root_directory = Path(subprocess.getoutput('git rev-parse --show-toplevel').strip())

    # Join the relative path with the given file_path
    return Path(file_path).resolve().relative_to(git_root_directory)

# Example usage:
# print(get_github_usernames_from_file('mkdocs.yml'))
