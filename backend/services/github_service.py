"""
GitHub service for cloning and fetching repository contents.
"""

from github import Github, GithubException
import git
import os
import shutil
import tempfile
from utils.helpers import parse_github_url


class GitHubService:
    """Service for interacting with GitHub repositories."""
    
    def __init__(self, access_token=None):
        """
        Initialize GitHub client.
        
        Args:
            access_token: Optional personal access token for private repos
        """
        self.access_token = access_token
        self.github_client = Github(access_token) if access_token else Github()
    
    def clone_repository(self, repo_url, branch='main', target_dir=None):
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch name (default: main)
            target_dir: Target directory (creates temp dir if None)
            
        Returns:
            str: Path to cloned repository
            
        Raises:
            Exception: If cloning fails
        """
        try:
            # Parse GitHub URL
            owner, repo_name = parse_github_url(repo_url)
            if not owner or not repo_name:
                raise ValueError("Invalid GitHub URL")
            
            # Create target directory
            if target_dir is None:
                target_dir = tempfile.mkdtemp(prefix=f"codedocs_{repo_name}_")
            else:
                os.makedirs(target_dir, exist_ok=True)
            
            # Build clone URL with token if provided
            # SECURITY: Never include token in logs or error messages
            if self.access_token:
                # Use OAuth token format (more secure than embedding in URL)
                clone_url = f"https://oauth2:{self.access_token}@github.com/{owner}/{repo_name}.git"
            else:
                clone_url = f"https://github.com/{owner}/{repo_name}.git"
            
            # Clone repository
            # SECURITY: Don't log the clone URL as it may contain credentials
            print(f"Cloning repository: {owner}/{repo_name} (branch: {branch})...")
            repo = git.Repo.clone_from(
                clone_url,
                target_dir,
                branch=branch,
                depth=1  # Shallow clone for faster download
            )
            
            print(f"Repository cloned successfully to temporary directory")
            return target_dir
        
        except git.GitCommandError as e:
            # SECURITY: Don't include exception details that might contain URLs with tokens
            print(f"Git clone failed for repository: {owner}/{repo_name}")
            raise Exception(f"Failed to clone repository. Please check your repository URL and access permissions.")
        except Exception as e:
            # SECURITY: Generic error message, no sensitive details
            print(f"Repository clone error for: {owner}/{repo_name}")
            raise Exception(f"Failed to clone repository. Please verify the repository URL and your access rights.")
    
    def get_repository_info(self, repo_url):
        """
        Get repository information using GitHub API.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            dict: Repository information
        """
        try:
            owner, repo_name = parse_github_url(repo_url)
            if not owner or not repo_name:
                raise ValueError("Invalid GitHub URL")
            
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'language': repo.language,
                'default_branch': repo.default_branch,
                'size': repo.size,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'private': repo.private,
            }
        
        except GithubException as e:
            print(f"GitHub API error: {e}")
            return None
    
    def get_file_tree(self, local_repo_path):
        """
        Get list of all files in cloned repository.
        
        Args:
            local_repo_path: Path to local repository
            
        Returns:
            list: List of file paths relative to repo root
        """
        files = []
        
        # Walk through directory
        for root, dirs, filenames in os.walk(local_repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            # Skip node_modules and other common directories
            skip_dirs = ['node_modules', '__pycache__', 'venv', 'env', '.venv', 'dist', 'build']
            for skip_dir in skip_dirs:
                if skip_dir in dirs:
                    dirs.remove(skip_dir)
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                # Get relative path
                rel_path = os.path.relpath(file_path, local_repo_path)
                files.append(rel_path)
        
        return files
    
    def read_file(self, repo_path, file_path):
        """
        Read file content from cloned repository.
        
        Args:
            repo_path: Path to local repository
            file_path: Relative path to file
            
        Returns:
            str: File content
        """
        try:
            full_path = os.path.join(repo_path, file_path)
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return content
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def cleanup_repo(self, repo_path):
        """
        Delete cloned repository directory.
        
        Args:
            repo_path: Path to repository
        """
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                print(f"Cleaned up repository at {repo_path}")
        except Exception as e:
            print(f"Error cleaning up repository: {e}")
    
    def validate_access(self, repo_url):
        """
        Validate access to repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            bool: True if accessible
        """
        try:
            owner, repo_name = parse_github_url(repo_url)
            if not owner or not repo_name:
                return False
            
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            # Try to access repo name (will fail if no access)
            _ = repo.name
            return True
        
        except GithubException:
            return False

