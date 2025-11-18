"""Data acquisition pipeline for orchestrating repository data collection."""

import re
from typing import Tuple, Optional
from datetime import datetime

from models.repository_data import RepositoryData
from data_acquisition.github_client import GitHubClient, GitHubAPIError
from data_acquisition.repo_analyzer import RepositoryAnalyzer
from utils.logger import get_logger


logger = get_logger(__name__)


class AcquisitionPipeline:
    """
    Orchestrates the data acquisition workflow.
    
    Coordinates GitHub API calls and local repository analysis to populate
    the Repository Data Model with all necessary information.
    """
    
    def __init__(
        self,
        github_client: GitHubClient,
        repo_analyzer: RepositoryAnalyzer
    ):
        """
        Initialize acquisition pipeline.
        
        Args:
            github_client: GitHub API client instance
            repo_analyzer: Repository analyzer instance
        """
        self.github_client = github_client
        self.repo_analyzer = repo_analyzer
    
    @staticmethod
    def parse_github_url(url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repository name.
        
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - github.com/owner/repo
        - owner/repo
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            ValueError: If URL format is invalid
        """
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Remove .git extension if present
        if url.endswith('.git'):
            url = url[:-4]
        
        # Pattern to match GitHub URLs
        patterns = [
            r'https?://github\.com/([^/]+)/(.+)',  # https://github.com/owner/repo
            r'github\.com/([^/]+)/(.+)',            # github.com/owner/repo
            r'^([^/]+)/(.+)$'                       # owner/repo
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                owner, repo = match.groups()
                logger.debug(f"Parsed URL: owner={owner}, repo={repo}")
                return owner, repo
        
        raise ValueError(
            f"Invalid GitHub URL format: {url}. "
            "Expected formats: 'https://github.com/owner/repo', 'github.com/owner/repo', or 'owner/repo'"
        )
    
    def execute(self, github_url: str) -> RepositoryData:
        """
        Execute the complete data acquisition workflow.
        
        Stages:
        1. Parse GitHub URL
        2. Fetch repository metadata from GitHub API
        3. Fetch commit activity and contributors
        4. Clone repository for local analysis
        5. Analyze file extensions and structure
        6. Select representative files for quality analysis
        7. Extract dependencies
        8. Populate Repository Data Model
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            RepositoryData instance populated with acquired data
            
        Raises:
            ValueError: If URL is invalid
            GitHubAPIError: If GitHub API requests fail
        """
        logger.info("=" * 80)
        logger.info("Starting Data Acquisition Pipeline")
        logger.info("=" * 80)
        
        # Initialize repository data model
        repo_data = RepositoryData()
        repo_data.github_url = github_url
        repo_data.analysis_date = datetime.now().isoformat()
        
        # Stage 1: Parse GitHub URL
        logger.info("Stage 1: Parsing GitHub URL")
        try:
            owner, repo_name = self.parse_github_url(github_url)
            repo_data.owner = owner
            repo_data.repo_name = repo_name
            logger.info(f"✓ Successfully parsed URL: {owner}/{repo_name}")
        except ValueError as e:
            logger.error(f"✗ Failed to parse GitHub URL: {e}")
            raise
        
        # Stage 2: Fetch repository metadata
        logger.info("Stage 2: Fetching repository metadata from GitHub API")
        try:
            repo_info = self.github_client.get_repository_info(owner, repo_name)
            
            # Populate metadata fields
            repo_data.description = repo_info.get('description', '') or ''
            repo_data.created_date = repo_info.get('created_at', '')
            repo_data.last_updated = repo_info.get('updated_at', '')
            repo_data.default_branch = repo_info.get('default_branch', 'main')
            repo_data.primary_language = repo_info.get('language', '') or ''
            repo_data.stars = repo_info.get('stargazers_count', 0)
            repo_data.forks = repo_info.get('forks_count', 0)
            repo_data.license = repo_info.get('license', {}).get('name', '') if repo_info.get('license') else ''
            
            logger.info(f"✓ Successfully fetched metadata: {repo_data.stars} stars, {repo_data.forks} forks")
        except GitHubAPIError as e:
            logger.error(f"✗ Failed to fetch repository metadata: {e}")
            raise
        
        # Stage 3: Fetch commit activity
        logger.info("Stage 3: Fetching commit activity")
        try:
            commit_data = self.github_client.get_commit_activity(owner, repo_name)
            repo_data.total_commits = commit_data.get('total_commits', 0)
            
            # Process weekly commit activity into monthly
            commit_activity = commit_data.get('commit_activity', [])
            if commit_activity:
                # Get the most recent commit timestamp
                # commit_activity is a list of weeks with 'week' (timestamp) and 'total' (commits)
                if commit_activity:
                    latest_week = max(commit_activity, key=lambda x: x.get('week', 0))
                    repo_data.last_commit = datetime.fromtimestamp(
                        latest_week.get('week', 0)
                    ).isoformat() if latest_week.get('week') else ''
                
                # Aggregate weekly data into monthly
                monthly_commits = {}
                for week_data in commit_activity:
                    week_timestamp = week_data.get('week', 0)
                    if week_timestamp:
                        month_key = datetime.fromtimestamp(week_timestamp).strftime('%Y-%m')
                        monthly_commits[month_key] = monthly_commits.get(month_key, 0) + week_data.get('total', 0)
                
                repo_data.monthly_commits = monthly_commits
            
            logger.info(f"✓ Successfully fetched commit activity: {repo_data.total_commits} total commits")
        except GitHubAPIError as e:
            logger.warning(f"⚠ Failed to fetch commit activity: {e}")
            # Continue with partial data
        
        # Stage 4: Fetch contributors
        logger.info("Stage 4: Fetching contributors")
        try:
            contributors = self.github_client.get_contributors(owner, repo_name)
            repo_data.contributors = len(contributors)
            logger.info(f"✓ Successfully fetched contributors: {repo_data.contributors} contributors")
        except GitHubAPIError as e:
            logger.warning(f"⚠ Failed to fetch contributors: {e}")
            # Continue with partial data
        
        # Stage 5: Fetch language statistics
        logger.info("Stage 5: Fetching language statistics")
        try:
            languages = self.github_client.get_languages(owner, repo_name)
            if languages:
                total_bytes = sum(languages.values())
                repo_data.language_breakdown = {
                    lang: round((bytes_count / total_bytes) * 100, 2)
                    for lang, bytes_count in languages.items()
                }
            logger.info(f"✓ Successfully fetched language statistics: {len(languages)} languages")
        except GitHubAPIError as e:
            logger.warning(f"⚠ Failed to fetch language statistics: {e}")
            # Continue with partial data
        
        # Stage 6: Fetch README content
        logger.info("Stage 6: Fetching README content")
        try:
            readme_content = self.github_client.get_readme_content(owner, repo_name)
            # Store README content for later quality analysis
            # We'll add this to code_samples for now
            if readme_content:
                repo_data.code_samples['README.md'] = readme_content
            logger.info(f"✓ Successfully fetched README: {len(readme_content)} characters")
        except GitHubAPIError as e:
            logger.warning(f"⚠ Failed to fetch README: {e}")
            # Continue without README
        
        # Stage 7: Fetch security files
        logger.info("Stage 7: Checking security files")
        try:
            security_status = self.github_client.check_security_files(owner, repo_name)
            # Store security status for later analysis
            # We'll use this in the analysis pipeline
            logger.info(f"✓ Successfully checked security files: {security_status}")
        except GitHubAPIError as e:
            logger.warning(f"⚠ Failed to check security files: {e}")
            # Continue without security info
        
        # Stage 8: Clone repository for local analysis
        logger.info("Stage 8: Cloning repository for local analysis")
        repo_path = None
        try:
            clone_url = f"https://github.com/{owner}/{repo_name}.git"
            # Clone with full history to analyze commit activity
            repo_path = self.repo_analyzer.clone_repository(clone_url, shallow=False)
            logger.info(
                f"✓ Successfully cloned repository to {repo_path}",
                extra={'stage': 'clone', 'status': 'success'}
            )
        except Exception as e:
            logger.warning(
                f"⚠ Failed to clone repository: {str(e)}",
                extra={
                    'stage': 'clone',
                    'status': 'failed',
                    'error_type': type(e).__name__,
                    'fallback_mode': 'API-only'
                }
            )
            logger.warning(
                "Continuing with API-only analysis (without local file inspection). "
                "Some metrics like file extension analysis and code quality sampling will be limited."
            )
            # Continue without local analysis - graceful degradation
        
        # Stage 8a: Analyze git history (if cloned)
        if repo_path:
            logger.info("Stage 8a: Analyzing git commit history")
            try:
                git_history = self.repo_analyzer.analyze_git_history(repo_path)
                
                # Override GitHub API data with accurate git history data
                if git_history['total_commits'] > 0:
                    repo_data.total_commits = git_history['total_commits']
                    repo_data.monthly_commits = git_history['monthly_commits']
                    if git_history['last_commit_date']:
                        repo_data.last_commit = git_history['last_commit_date']
                    
                    logger.info(f"✓ Successfully analyzed git history: {repo_data.total_commits} total commits")
                else:
                    logger.warning("⚠ Git history analysis returned 0 commits")
            except Exception as e:
                logger.warning(f"⚠ Failed to analyze git history: {e}")
        
        # Stage 9: Analyze file extensions (if cloned)
        if repo_path:
            logger.info("Stage 9: Analyzing file extensions")
            try:
                extension_counts = self.repo_analyzer.analyze_file_extensions(repo_path)
                repo_data.file_extension_counts = extension_counts
                logger.info(f"✓ Successfully analyzed file extensions: {len(extension_counts)} unique extensions")
            except Exception as e:
                logger.warning(f"⚠ Failed to analyze file extensions: {e}")
        
        # Stage 10: Select files for quality analysis (if cloned)
        if repo_path:
            logger.info("Stage 10: Selecting files for quality analysis")
            try:
                selected_files = self.repo_analyzer.select_files_for_analysis(repo_path, max_files=5)
                repo_data.analyzed_files = selected_files
                logger.info(f"✓ Successfully selected {len(selected_files)} files for analysis")
                
                # Read file contents
                if selected_files:
                    logger.info("Stage 10a: Reading file contents")
                    file_contents = self.repo_analyzer.read_file_contents(repo_path, selected_files)
                    # Merge with existing code_samples (README)
                    repo_data.code_samples.update(file_contents)
                    logger.info(f"✓ Successfully read {len(file_contents)} files")
            except Exception as e:
                logger.warning(f"⚠ Failed to select/read files: {e}")
        
        # Stage 11: Extract dependencies (if cloned)
        if repo_path:
            logger.info("Stage 11: Extracting dependencies")
            try:
                dependencies = self.repo_analyzer.extract_dependencies(repo_path)
                repo_data.core_dependencies = dependencies
                logger.info(f"✓ Successfully extracted {len(dependencies)} dependencies")
            except Exception as e:
                logger.warning(f"⚠ Failed to extract dependencies: {e}")
        
        # Stage 12: Cleanup temporary files
        if repo_path:
            logger.info("Stage 12: Cleaning up temporary files")
            try:
                self.repo_analyzer.cleanup(repo_path)
                logger.info("✓ Successfully cleaned up temporary files")
            except Exception as e:
                logger.warning(f"⚠ Failed to cleanup temporary files: {e}")
        
        logger.info("=" * 80)
        logger.info("Data Acquisition Pipeline Complete")
        logger.info(f"Repository: {owner}/{repo_name}")
        logger.info(f"Stars: {repo_data.stars}, Forks: {repo_data.forks}, Contributors: {repo_data.contributors}")
        logger.info(f"Total Commits: {repo_data.total_commits}")
        logger.info(f"File Extensions: {len(repo_data.file_extension_counts)}")
        logger.info(f"Analyzed Files: {len(repo_data.analyzed_files)}")
        logger.info(f"Dependencies: {len(repo_data.core_dependencies)}")
        logger.info("=" * 80)
        
        return repo_data
