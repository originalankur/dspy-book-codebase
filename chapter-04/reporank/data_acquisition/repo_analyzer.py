"""Repository analyzer for local repository analysis."""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """
    Analyzes local repository structure and content.
    
    Provides methods for:
    - Cloning repositories
    - Analyzing file extensions
    - Selecting representative files for quality analysis
    - Reading file contents
    - Extracting dependencies
    """
    
    def __init__(self, clone_timeout: int = 300, temp_dir: str = "/tmp/reporank"):
        """
        Initialize repository analyzer.
        
        Args:
            clone_timeout: Timeout in seconds for clone operations (default: 300)
            temp_dir: Base directory for temporary clones (default: /tmp/reporank)
        """
        self.clone_timeout = clone_timeout
        self.temp_dir = temp_dir
        self._cloned_paths: List[str] = []
        
        if not GIT_AVAILABLE:
            logger.warning("GitPython not available. Repository cloning will be disabled.")
    
    def clone_repository(self, url: str, target_dir: Optional[str] = None, shallow: bool = False) -> str:
        """
        Clone a Git repository to a temporary directory.
        
        Args:
            url: Git repository URL (e.g., https://github.com/owner/repo.git)
            target_dir: Optional target directory. If None, creates a temp directory.
            shallow: If True, performs shallow clone (depth=1). Default False for full history.
            
        Returns:
            Path to the cloned repository
            
        Raises:
            RuntimeError: If GitPython is not available
            GitCommandError: If cloning fails
            TimeoutError: If cloning exceeds timeout
        """
        if not GIT_AVAILABLE:
            raise RuntimeError(
                "GitPython is not installed. Install it with: pip install gitpython"
            )
        
        # Create target directory if not provided
        if target_dir is None:
            os.makedirs(self.temp_dir, exist_ok=True)
            target_dir = tempfile.mkdtemp(dir=self.temp_dir, prefix="repo_")
        
        clone_type = "shallow" if shallow else "full"
        logger.info(
            f"Cloning repository ({clone_type}) from {url} to {target_dir}",
            extra={
                'clone_type': clone_type,
                'url': url,
                'target_dir': target_dir,
                'timeout': self.clone_timeout
            }
        )
        
        try:
            # Clone with or without depth limit
            clone_kwargs = {
                'url': url,
                'to_path': target_dir,
                'single_branch': True,  # Only clone default branch
            }
            
            if shallow:
                clone_kwargs['depth'] = 1  # Shallow clone for faster cloning
            
            repo = Repo.clone_from(**clone_kwargs)
            
            self._cloned_paths.append(target_dir)
            logger.info(
                f"Successfully cloned repository to {target_dir}",
                extra={'target_dir': target_dir, 'clone_type': clone_type}
            )
            return target_dir
            
        except GitCommandError as e:
            error_msg = (
                f"Git clone failed: {str(e)}. "
                f"This could be due to: "
                f"1) Repository is too large, "
                f"2) Network connectivity issues, "
                f"3) Invalid repository URL, or "
                f"4) Authentication required for private repository. "
                f"Analysis will continue with API-only mode."
            )
            logger.error(
                error_msg,
                extra={
                    'url': url,
                    'error_type': 'GitCommandError',
                    'error_details': str(e),
                    'fallback': 'API-only mode'
                }
            )
            # Clean up failed clone directory
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup directory {target_dir}: {cleanup_error}")
            raise RuntimeError(error_msg) from e
            
        except Exception as e:
            error_msg = (
                f"Unexpected error during repository clone: {str(e)}. "
                f"Analysis will continue with API-only mode (without local file analysis)."
            )
            logger.error(
                error_msg,
                extra={
                    'url': url,
                    'error_type': type(e).__name__,
                    'error_details': str(e),
                    'fallback': 'API-only mode'
                },
                exc_info=True
            )
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup directory {target_dir}: {cleanup_error}")
            raise RuntimeError(error_msg) from e
    
    def cleanup(self, repo_path: Optional[str] = None) -> None:
        """
        Remove temporary directories created during analysis.
        
        Args:
            repo_path: Specific path to clean up. If None, cleans all tracked paths.
        """
        if repo_path:
            paths_to_clean = [repo_path]
        else:
            paths_to_clean = self._cloned_paths.copy()
        
        for path in paths_to_clean:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    logger.info(f"Cleaned up temporary directory: {path}")
                    if path in self._cloned_paths:
                        self._cloned_paths.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to clean up {path}: {e}")
    
    def analyze_file_extensions(self, repo_path: str) -> Dict[str, int]:
        """
        Walk repository and count file extensions.
        
        Skips common non-code directories like .git, node_modules, venv, etc.
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Dictionary mapping extensions to counts, e.g., {'.py': 150, '.js': 45}
        """
        extension_counts: Dict[str, int] = {}
        
        # Directories to skip
        skip_dirs = {
            '.git', 'node_modules', 'venv', '__pycache__', 
            'dist', 'build', '.venv', 'env', '.env',
            'target', 'bin', 'obj', '.idea', '.vscode'
        }
        
        logger.info(f"Analyzing file extensions in {repo_path}")
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out directories to skip (modifies dirs in-place)
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:  # Only count files with extensions
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        logger.info(f"Found {len(extension_counts)} unique file extensions")
        return extension_counts

    def select_files_for_analysis(
        self, 
        repo_path: str, 
        max_files: int = 5
    ) -> List[str]:
        """
        Select the largest source code files for quality analysis.
        
        Prioritizes code files and skips test files, minified files, and generated code.
        
        Args:
            repo_path: Path to the repository root
            max_files: Maximum number of files to select (default: 5)
            
        Returns:
            List of file paths (relative to repo_path) sorted by size (largest first)
        """
        # Code extensions to prioritize
        code_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.go', '.rs', '.cpp', '.c', 
            '.rb', '.php', '.cs', '.swift', '.kt'
        }
        
        # Patterns to skip
        skip_patterns = [
            'test', 'spec', '.min.', 'vendor', 'generated',
            '.bundle.', 'dist/', 'build/', '__pycache__'
        ]
        
        # Directories to skip
        skip_dirs = {
            '.git', 'node_modules', 'venv', '__pycache__', 
            'dist', 'build', '.venv', 'env', '.env',
            'target', 'bin', 'obj', '.idea', '.vscode',
            'tests', 'test', '__tests__', 'spec'
        }
        
        file_sizes: List[Tuple[str, int]] = []
        
        logger.info(f"Selecting files for analysis from {repo_path}")
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                
                # Only consider files with code extensions
                if ext not in code_extensions:
                    continue
                
                # Skip files matching skip patterns
                file_lower = file.lower()
                if any(pattern in file_lower for pattern in skip_patterns):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    # Count lines of code
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                    
                    # Get relative path from repo root
                    rel_path = os.path.relpath(file_path, repo_path)
                    file_sizes.append((rel_path, line_count))
                    
                except Exception as e:
                    logger.debug(f"Could not read file {file_path}: {e}")
                    continue
        
        # Sort by line count (descending) and take top N
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        selected_files = [path for path, _ in file_sizes[:max_files]]
        
        logger.info(f"Selected {len(selected_files)} files for analysis")
        return selected_files

    def read_file_contents(
        self, 
        repo_path: str, 
        file_paths: List[str]
    ) -> Dict[str, str]:
        """
        Read contents of selected files.
        
        Handles encoding errors gracefully using utf-8 with error ignore.
        
        Args:
            repo_path: Path to the repository root
            file_paths: List of file paths relative to repo_path
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        contents: Dict[str, str] = {}
        
        logger.info(f"Reading contents of {len(file_paths)} files")
        
        for file_path in file_paths:
            full_path = os.path.join(repo_path, file_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    contents[file_path] = content
                    logger.debug(f"Read {len(content)} characters from {file_path}")
                    
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                contents[file_path] = f"[Error reading file: {e}]"
        
        logger.info(f"Successfully read {len(contents)} files")
        return contents

    def extract_dependencies(self, repo_path: str) -> List[Dict[str, str]]:
        """
        Extract dependencies from common dependency files.
        
        Detects and parses:
        - requirements.txt (Python)
        - package.json (Node.js)
        - go.mod (Go)
        - Cargo.toml (Rust)
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            List of dependency dictionaries with 'name', 'version', and 'ecosystem' keys
        """
        dependencies: List[Dict[str, str]] = []
        
        logger.info(f"Extracting dependencies from {repo_path}")
        
        # Python: requirements.txt
        req_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            deps = self._parse_requirements_txt(req_file)
            dependencies.extend(deps)
            logger.info(f"Found {len(deps)} Python dependencies")
        
        # Node.js: package.json
        pkg_file = os.path.join(repo_path, 'package.json')
        if os.path.exists(pkg_file):
            deps = self._parse_package_json(pkg_file)
            dependencies.extend(deps)
            logger.info(f"Found {len(deps)} Node.js dependencies")
        
        # Go: go.mod
        go_file = os.path.join(repo_path, 'go.mod')
        if os.path.exists(go_file):
            deps = self._parse_go_mod(go_file)
            dependencies.extend(deps)
            logger.info(f"Found {len(deps)} Go dependencies")
        
        # Rust: Cargo.toml
        cargo_file = os.path.join(repo_path, 'Cargo.toml')
        if os.path.exists(cargo_file):
            deps = self._parse_cargo_toml(cargo_file)
            dependencies.extend(deps)
            logger.info(f"Found {len(deps)} Rust dependencies")
        
        logger.info(f"Total dependencies extracted: {len(dependencies)}")
        return dependencies
    
    def _parse_requirements_txt(self, file_path: str) -> List[Dict[str, str]]:
        """Parse Python requirements.txt file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip editable installs and URLs
                    if line.startswith('-e') or line.startswith('http'):
                        continue
                    
                    # Parse package name and version
                    # Handle formats: package==1.0.0, package>=1.0.0, package
                    for sep in ['==', '>=', '<=', '~=', '!=', '<', '>']:
                        if sep in line:
                            name, version = line.split(sep, 1)
                            dependencies.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'ecosystem': 'Python'
                            })
                            break
                    else:
                        # No version specified
                        dependencies.append({
                            'name': line.strip(),
                            'version': 'unspecified',
                            'ecosystem': 'Python'
                        })
        except Exception as e:
            logger.warning(f"Error parsing requirements.txt: {e}")
        
        return dependencies
    
    def _parse_package_json(self, file_path: str) -> List[Dict[str, str]]:
        """Parse Node.js package.json file."""
        dependencies = []
        
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            # Extract dependencies and devDependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data and isinstance(data[dep_type], dict):
                    for name, version in data[dep_type].items():
                        dependencies.append({
                            'name': name,
                            'version': version,
                            'ecosystem': 'Node.js'
                        })
        except Exception as e:
            logger.warning(f"Error parsing package.json: {e}")
        
        return dependencies
    
    def _parse_go_mod(self, file_path: str) -> List[Dict[str, str]]:
        """Parse Go go.mod file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                in_require_block = False
                
                for line in f:
                    line = line.strip()
                    
                    # Detect require block
                    if line.startswith('require ('):
                        in_require_block = True
                        continue
                    elif line == ')' and in_require_block:
                        in_require_block = False
                        continue
                    
                    # Parse single require or require block entry
                    if line.startswith('require ') or in_require_block:
                        # Remove 'require ' prefix if present
                        if line.startswith('require '):
                            line = line[8:]
                        
                        # Skip empty lines and comments
                        if not line or line.startswith('//'):
                            continue
                        
                        # Parse: module version
                        parts = line.split()
                        if len(parts) >= 2:
                            dependencies.append({
                                'name': parts[0],
                                'version': parts[1],
                                'ecosystem': 'Go'
                            })
        except Exception as e:
            logger.warning(f"Error parsing go.mod: {e}")
        
        return dependencies
    
    def _parse_cargo_toml(self, file_path: str) -> List[Dict[str, str]]:
        """Parse Rust Cargo.toml file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                in_dependencies = False
                
                for line in f:
                    line = line.strip()
                    
                    # Detect [dependencies] section
                    if line == '[dependencies]':
                        in_dependencies = True
                        continue
                    elif line.startswith('[') and in_dependencies:
                        # New section started
                        in_dependencies = False
                        continue
                    
                    # Parse dependency in [dependencies] section
                    if in_dependencies and '=' in line:
                        # Skip comments
                        if line.startswith('#'):
                            continue
                        
                        # Parse: name = "version" or name = { version = "version" }
                        name, rest = line.split('=', 1)
                        name = name.strip()
                        rest = rest.strip()
                        
                        # Extract version
                        version = 'unspecified'
                        if rest.startswith('"'):
                            # Simple format: name = "version"
                            version = rest.strip('"').strip("'")
                        elif 'version' in rest:
                            # Complex format: name = { version = "version" }
                            import re
                            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', rest)
                            if match:
                                version = match.group(1)
                        
                        dependencies.append({
                            'name': name,
                            'version': version,
                            'ecosystem': 'Rust'
                        })
        except Exception as e:
            logger.warning(f"Error parsing Cargo.toml: {e}")
        
        return dependencies
    
    def analyze_git_history(self, repo_path: str) -> Dict[str, any]:
        """
        Analyze git commit history from cloned repository.
        
        Extracts:
        - Total commit count
        - Monthly commit breakdown for last 12 months
        - Last commit date
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Dictionary with 'total_commits', 'monthly_commits', and 'last_commit_date'
        """
        
        logger.info(f"Analyzing git history in {repo_path}")
        
        if not GIT_AVAILABLE:
            logger.warning("GitPython not available, cannot analyze git history")
            return {
                'total_commits': 0,
                'monthly_commits': {},
                'last_commit_date': None
            }
        
        try:
            repo = Repo(repo_path)
            
            # Get all commits
            commits = list(repo.iter_commits())
            total_commits = len(commits)
            
            # Calculate date 12 months ago
            twelve_months_ago = datetime.now() - timedelta(days=365)
            
            # Count commits per month for last 12 months
            monthly_commits = defaultdict(int)
            last_commit_date = None
            
            for commit in commits:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                
                # Track last commit date
                if last_commit_date is None or commit_date > last_commit_date:
                    last_commit_date = commit_date
                
                # Only count commits from last 12 months
                if commit_date >= twelve_months_ago:
                    month_key = commit_date.strftime('%Y-%m')
                    monthly_commits[month_key] += 1
            
            logger.info(f"Found {total_commits} total commits, {len(monthly_commits)} months with activity")
            
            return {
                'total_commits': total_commits,
                'monthly_commits': dict(monthly_commits),
                'last_commit_date': last_commit_date.isoformat() if last_commit_date else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing git history: {e}")
            return {
                'total_commits': 0,
                'monthly_commits': {},
                'last_commit_date': None
            }
