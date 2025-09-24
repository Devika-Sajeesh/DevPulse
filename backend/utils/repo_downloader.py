from git import Repo

def clone_repo(url, path):
    Repo.clone_from(url, path)
    return path
