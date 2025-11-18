"""GitHub API client for repository data acquisition."""

import time
from typing import Dict, List, Optional, Any
import requests

from utils.logger import get_logger


logger = get_logger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded."""
    
    def __init__(self, message: str, reset_time: Optional[int] = None):
        super().__init__(message)
        self.reset_time = reset_time


class GitHubClient:
    """
    Client for interacting with GitHub REST API.
    
    Supports both authenticated and unauthenticated requests.
    - Unauthenticated: 60 requests/hour
    - Authenticated: 5,000 requests/hour
    
    Implements retry logic with exponential backoff for transient failures.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize GitHub API client.
        
        Args:
            token: Optional GitHub personal access token for authentication
            base_url: GitHub API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RepoRank/0.1.0'
        })
        
        if self.token:
            self.session.headers['Authorization'] = f'token {self.token}'
            logger.info("GitHub client initialized with authentication")
        else:
            logger.info("GitHub client initialized without authentication (60 req/hr limit)")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and rate limit handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            RateLimitError: When rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault('timeout', self.timeout)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.request(method, url, **kwargs)
                
                # Check for rate limiting
                if response.status_code == 403:
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                    if rate_limit_remaining == '0':
                        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                        reset_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
                        error_msg = f"GitHub API rate limit exceeded. Resets at {reset_datetime}"
                        logger.error(error_msg, extra={
                            'reset_time': reset_time,
                            'reset_datetime': reset_datetime
                        })
                        raise RateLimitError(error_msg, reset_time)
                
                # Check for other client/server errors
                if response.status_code == 404:
                    logger.warning(f"Resource not found: {endpoint}")
                    response.raise_for_status()
                elif response.status_code == 401:
                    logger.error("Authentication failed - invalid or missing GitHub token")
                    response.raise_for_status()
                elif response.status_code >= 400:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                
                # Log rate limit info
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
                rate_limit_limit = response.headers.get('X-RateLimit-Limit')
                if rate_limit_remaining and rate_limit_limit:
                    logger.debug(f"Rate limit: {rate_limit_remaining}/{rate_limit_limit} remaining")
                
                return response
                
            except requests.exceptions.Timeout as e:
                wait_time = 2 ** attempt
                logger.warning(
                    f"Request timeout on attempt {attempt + 1}/{self.max_retries}",
                    extra={
                        'attempt': attempt + 1,
                        'max_retries': self.max_retries,
                        'wait_time': wait_time,
                        'endpoint': endpoint
                    }
                )
                if attempt == self.max_retries - 1:
                    error_msg = (
                        f"Request timed out after {self.max_retries} attempts. "
                        f"The GitHub API may be slow or unreachable. "
                        f"Please check your network connection and try again."
                    )
                    logger.error(error_msg, extra={'endpoint': endpoint})
                    raise GitHubAPIError(error_msg) from e
                time.sleep(wait_time)  # Exponential backoff
                
            except requests.exceptions.ConnectionError as e:
                wait_time = 2 ** attempt
                logger.warning(
                    f"Network connection error on attempt {attempt + 1}/{self.max_retries}",
                    extra={
                        'attempt': attempt + 1,
                        'max_retries': self.max_retries,
                        'wait_time': wait_time,
                        'endpoint': endpoint,
                        'error_type': type(e).__name__
                    }
                )
                if attempt == self.max_retries - 1:
                    error_msg = (
                        f"Network connection failed after {self.max_retries} attempts. "
                        f"Please check your internet connection and try again. "
                        f"Error: {str(e)}"
                    )
                    logger.error(error_msg, extra={'endpoint': endpoint})
                    raise GitHubAPIError(error_msg) from e
                time.sleep(wait_time)  # Exponential backoff
                
            except requests.exceptions.HTTPError as e:
                # Don't retry on client errors (4xx except 429)
                if e.response.status_code == 429:  # Too Many Requests
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                raise GitHubAPIError(f"HTTP error: {e}") from e
        
        raise GitHubAPIError(f"Request failed after {self.max_retries} attempts")
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch repository metadata from GitHub API.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Returns:
            Dictionary containing repository metadata including:
            - name, description, created_at, updated_at
            - stargazers_count, forks_count, watchers_count
            - default_branch, language, license
            - open_issues_count, has_wiki, has_pages
            
        Raises:
            GitHubAPIError: If the request fails
        """
        logger.info(f"Fetching repository info for {owner}/{repo}")
        
        try:
            response = self._make_request('GET', f'/repos/{owner}/{repo}')
            data = response.json()
            
            logger.info(f"Successfully fetched info for {owner}/{repo}")
            logger.debug(f"Repository has {data.get('stargazers_count', 0)} stars")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch repository info for {owner}/{repo}: {e}")
            raise
    
    def get_commit_activity(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch commit activity statistics for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing:
            - total_commits: Total number of commits
            - commit_activity: Weekly commit activity for the past year
            
        Raises:
            GitHubAPIError: If the request fails
        """
        logger.info(f"Fetching commit activity for {owner}/{repo}")
        
        try:
            # Get total commit count from contributors endpoint
            contributors_response = self._make_request(
                'GET',
                f'/repos/{owner}/{repo}/contributors',
                params={'per_page': 1, 'anon': 'true'}
            )
            
            # Total commits is sum of all contributor commits
            # For efficiency, we'll get it from the first page link header
            total_commits = 0
            try:
                # Try to get from stats/contributors for more accurate count
                stats_response = self._make_request(
                    'GET',
                    f'/repos/{owner}/{repo}/stats/contributors'
                )
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if stats_data:
                        total_commits = sum(contributor.get('total', 0) for contributor in stats_data)
            except Exception as e:
                logger.warning(f"Could not fetch detailed commit stats: {e}")
            
            # Get weekly commit activity
            # This is like a fall back coz we will do an analysis of the repo
            # and get the commits
            activity_response = self._make_request(
                'GET',
                f'/repos/{owner}/{repo}/stats/commit_activity'
            )
            
            commit_activity = []
            if activity_response.status_code == 200:
                commit_activity = activity_response.json() or []
            
            logger.info(f"Successfully fetched commit activity for {owner}/{repo}")
            
            return {
                'total_commits': total_commits,
                'commit_activity': commit_activity
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch commit activity for {owner}/{repo}: {e}")
            raise
    
    def get_contributors(self, owner: str, repo: str, max_contributors: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch list of repository contributors.
        
        Args:
            owner: Repository owner
            repo: Repository name
            max_contributors: Maximum number of contributors to fetch
            
        Returns:
            List of contributor dictionaries containing:
            - login, contributions, type
            - avatar_url, html_url
            
        Raises:
            GitHubAPIError: If the request fails
        """
        logger.info(f"Fetching contributors for {owner}/{repo}")
        
        try:
            response = self._make_request(
                'GET',
                f'/repos/{owner}/{repo}/contributors',
                params={
                    'per_page': min(max_contributors, 100),
                    'anon': 'true'
                }
            )
            
            contributors = response.json()
            logger.info(f"Successfully fetched {len(contributors)} contributors for {owner}/{repo}")
            
            return contributors
            
        except Exception as e:
            logger.error(f"Failed to fetch contributors for {owner}/{repo}: {e}")
            raise
    
    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Fetch language statistics for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary mapping language names to bytes of code:
            {'Python': 125000, 'JavaScript': 50000, ...}
            
        Raises:
            GitHubAPIError: If the request fails
        """
        logger.info(f"Fetching language statistics for {owner}/{repo}")
        
        try:
            response = self._make_request('GET', f'/repos/{owner}/{repo}/languages')
            languages = response.json()
            
            logger.info(f"Successfully fetched {len(languages)} languages for {owner}/{repo}")
            logger.debug(f"Languages: {list(languages.keys())}")
            
            return languages
            
        except Exception as e:
            logger.error(f"Failed to fetch languages for {owner}/{repo}: {e}")
            raise
    
    def check_security_files(self, owner: str, repo: str) -> Dict[str, bool]:
        """
        Check for presence of security-related files and configurations.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary indicating presence of security features:
            {
                'has_security_md': bool,
                'has_security_policy': bool,
                'has_dependabot': bool,
                'has_code_scanning': bool
            }
            
        Raises:
            GitHubAPIError: If the request fails
        """
        logger.info(f"Checking security files for {owner}/{repo}")
        
        security_status = {
            'has_security_md': False,
            'has_security_policy': False,
            'has_dependabot': False,
            'has_code_scanning': False
        }
        
        try:
            # Check for SECURITY.md in common locations
            security_paths = ['SECURITY.md', '.github/SECURITY.md', 'docs/SECURITY.md']
            for path in security_paths:
                try:
                    response = self._make_request(
                        'GET',
                        f'/repos/{owner}/{repo}/contents/{path}'
                    )
                    if response.status_code == 200:
                        security_status['has_security_md'] = True
                        security_status['has_security_policy'] = True
                        logger.debug(f"Found SECURITY.md at {path}")
                        break
                except GitHubAPIError:
                    continue
            
            # Check for Dependabot configuration
            dependabot_paths = ['.github/dependabot.yml', '.github/dependabot.yaml']
            for path in dependabot_paths:
                try:
                    response = self._make_request(
                        'GET',
                        f'/repos/{owner}/{repo}/contents/{path}'
                    )
                    if response.status_code == 200:
                        security_status['has_dependabot'] = True
                        logger.debug(f"Found Dependabot config at {path}")
                        break
                except GitHubAPIError:
                    continue
            
            # Check for code scanning alerts (requires authentication)
            if self.token:
                try:
                    response = self._make_request(
                        'GET',
                        f'/repos/{owner}/{repo}/code-scanning/alerts',
                        params={'per_page': 1}
                    )
                    # If we get a 200, code scanning is enabled (even if no alerts)
                    if response.status_code == 200:
                        security_status['has_code_scanning'] = True
                        logger.debug("Code scanning is enabled")
                except GitHubAPIError:
                    # 404 or 403 means code scanning is not enabled or not accessible
                    pass
            
            logger.info(f"Security check complete for {owner}/{repo}: {security_status}")
            return security_status
            
        except Exception as e:
            logger.error(f"Failed to check security files for {owner}/{repo}: {e}")
            # Return partial results rather than failing completely
            return security_status
    
    def get_readme_content(self, owner: str, repo: str) -> str:
        """
        Fetch README content for quality analysis.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string (decoded from base64)
            Returns empty string if README not found
            
        Raises:
            GitHubAPIError: If the request fails (except 404)
        """
        logger.info(f"Fetching README content for {owner}/{repo}")
        
        try:
            response = self._make_request('GET', f'/repos/{owner}/{repo}/readme')
            
            if response.status_code == 404:
                logger.warning(f"No README found for {owner}/{repo}")
                return ""
            
            readme_data = response.json()
            
            # README content is base64 encoded
            import base64
            content = readme_data.get('content', '')
            if content:
                decoded_content = base64.b64decode(content).decode('utf-8', errors='ignore')
                logger.info(f"Successfully fetched README for {owner}/{repo} ({len(decoded_content)} characters)")
                return decoded_content
            
            return ""
            
        except GitHubAPIError as e:
            # If it's a 404, return empty string
            if "404" in str(e):
                logger.warning(f"No README found for {owner}/{repo}")
                return ""
            logger.error(f"Failed to fetch README for {owner}/{repo}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch README for {owner}/{repo}: {e}")
            raise
