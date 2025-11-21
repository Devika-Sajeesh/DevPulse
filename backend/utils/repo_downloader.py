"""
Repository downloader with retry logic and validation.

Handles Git repository cloning with comprehensive error handling,
retry logic, and validation.
"""

from typing import Tuple, Optional
from git import Repo, GitCommandError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.utils.logger import setup_logger
from backend.utils.exceptions import RepositoryError
from backend.utils.validators import validate_github_url

logger = setup_logger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(GitCommandError),
    reraise=True
)
def clone_repo(url: str, path: str, shallow: bool = True) -> Tuple[str, str]:
    """
    Clone a Git repository with retry logic.
    
    Args:
        url: Repository URL to clone
        path: Local path to clone into
        shallow: Whether to perform shallow clone (faster, less data)
    
    Returns:
        Tuple of (cloned_path, commit_sha)
    
    Raises:
        RepositoryError: If cloning fails after retries
    """
    try:
        # Validate URL before attempting clone
        validated_url = validate_github_url(url)
        logger.info(f"Cloning repository: {validated_url} to {path}")
        
        # Clone with optional shallow clone for performance
        clone_kwargs = {
            'depth': 1,
            'single_branch': True
        } if shallow else {}
        
        repo = Repo.clone_from(validated_url, path, **clone_kwargs)
        
        # Get the latest commit SHA
        commit_sha = repo.head.commit.hexsha
        
        logger.info(
            f"Successfully cloned repository: {validated_url}",
            extra={'extra_data': {
                'commit_sha': commit_sha,
                'shallow': shallow
            }}
        )
        
        return path, commit_sha
        
    except GitCommandError as e:
        logger.error(
            f"Git command failed while cloning {url}: {e}",
            exc_info=True
        )
        raise RepositoryError(
            f"Failed to clone repository: {str(e)}",
            repo_url=url,
            details={'git_error': str(e)}
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while cloning {url}: {e}",
            exc_info=True
        )
        raise RepositoryError(
            f"Repository cloning failed: {str(e)}",
            repo_url=url,
            details={'error_type': type(e).__name__}
        )


def get_repo_info(repo_path: str) -> dict:
    """
    Get information about a cloned repository.
    
    Args:
        repo_path: Path to the cloned repository
    
    Returns:
        Dictionary with repository information
    
    Raises:
        RepositoryError: If repository is invalid
    """
    try:
        repo = Repo(repo_path)
        
        return {
            'commit_sha': repo.head.commit.hexsha,
            'commit_message': repo.head.commit.message.strip(),
            'author': str(repo.head.commit.author),
            'commit_date': repo.head.commit.committed_datetime.isoformat(),
            'branch': repo.active_branch.name if not repo.head.is_detached else 'detached',
            'remote_url': repo.remotes.origin.url if repo.remotes else None
        }
    except Exception as e:
        logger.error(f"Failed to get repo info for {repo_path}: {e}")
        raise RepositoryError(
            f"Failed to read repository information: {str(e)}",
            details={'repo_path': repo_path}
        )