# backend/utils/repo_downloader.py

from git import Repo

def clone_repo(url, path):
    # Clone the repository
    repo = Repo.clone_from(url, path)
    # Get the latest commit SHA
    commit_sha = repo.head.commit.hexsha
    # Return the path and the SHA
    return path, commit_sha