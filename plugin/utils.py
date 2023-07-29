import subprocess
from collections import Counter
from pathlib import Path
import requests
import yaml  # install this with `pip install PyYAML` if not installed yet


def get_github_username_from_email(email, local_cache):
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
    print(f'Running GitHub REST API for {email}')
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] > 0:
            username = data['items'][0]['login']
            local_cache[email] = username  # save the username in the local cache for future use
            return username

    print(f'WARNING: No username found for {email}')
    return None  # couldn't find username


def get_github_usernames_from_file(file_path):
    authors_emails = subprocess.check_output(['git', 'log', '--pretty=format:%ae', Path(file_path).resolve()]).decode(
        'utf-8').split('\n')
    emails = dict(Counter(authors_emails))  # dict of {author: changes}

    # Load the local cache of GitHub usernames
    local_cache_file = Path('mkdocs_github_authors.yaml')
    if local_cache_file.is_file():
        with local_cache_file.open('r') as f:
            local_cache = yaml.safe_load(f)
    else:
        local_cache = {}

    info = {}
    for k, v in emails.items():
        username = get_github_username_from_email(k, local_cache)
        if username:
            info[username] = {'email': k, 'url': f'https://github.com/{username}', 'changes': v}

    # Save the local cache of GitHub usernames
    with local_cache_file.open('w') as f:
        yaml.safe_dump(local_cache, f)

    return info


# Example usage:
# print(get_github_usernames_from_file('mkdocs.yml'))
