# Data Acquisition Module

This module handles fetching and analyzing repository data from GitHub and local sources.

## Components

### GitHubClient (`github_client.py`)
Handles all interactions with the GitHub REST API:
- Repository metadata fetching
- Commit activity analysis
- Contributor information
- Language statistics
- Security file detection
- Rate limit handling with exponential backoff

### RepositoryAnalyzer (`repo_analyzer.py`)
Analyzes local repository structure and content:
- Repository cloning with GitPython
- File extension analysis
- Smart file selection for code quality analysis
- File content reading
- Dependency extraction from multiple ecosystems

## Usage Examples

### Analyzing File Extensions

```python
from reporank.data_acquisition import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
extensions = analyzer.analyze_file_extensions('/path/to/repo')

# Returns: {'.py': 150, '.js': 45, '.md': 12, ...}
```

### Selecting Files for Analysis

```python
# Select the 5 largest source code files
selected_files = analyzer.select_files_for_analysis('/path/to/repo', max_files=5)

# Returns: ['src/main.py', 'lib/core.py', ...]
```

### Reading File Contents

```python
# Read contents of selected files
contents = analyzer.read_file_contents('/path/to/repo', selected_files)

# Returns: {'src/main.py': '# file content...', ...}
```

### Extracting Dependencies

```python
# Extract dependencies from requirements.txt, package.json, etc.
dependencies = analyzer.extract_dependencies('/path/to/repo')

# Returns: [
#   {'name': 'requests', 'version': '2.31.0', 'ecosystem': 'Python'},
#   {'name': 'express', 'version': '^4.18.0', 'ecosystem': 'Node.js'},
#   ...
# ]
```

### Cloning Repositories

```python
# Clone a repository (requires GitPython)
repo_path = analyzer.clone_repository('https://github.com/owner/repo.git')

# Perform analysis...

# Clean up when done
analyzer.cleanup(repo_path)
```

## Supported Dependency Files

- **Python**: `requirements.txt`
- **Node.js**: `package.json` (dependencies and devDependencies)
- **Go**: `go.mod`
- **Rust**: `Cargo.toml`

## Error Handling

The module includes comprehensive error handling:
- Graceful degradation when GitPython is not available
- Encoding error handling for file reading (utf-8 with ignore)
- Logging of warnings for failed operations
- Cleanup of temporary directories on errors

## Configuration

Configure the analyzer through the Config class:

```python
from reporank.config import Config

config = Config(
    clone_timeout=300,  # 5 minutes
    temp_dir='/tmp/reporank',
    enable_local_clone=True
)

analyzer = RepositoryAnalyzer(
    clone_timeout=config.clone_timeout,
    temp_dir=config.temp_dir
)
```

## Requirements

- `requests>=2.31.0` - For GitHub API calls
- `gitpython>=3.1.40` - For repository cloning (optional)

## Notes

- Repository cloning uses shallow clones (depth=1) for faster performance
- Non-code directories (.git, node_modules, venv, etc.) are automatically skipped
- Test files, minified files, and generated code are excluded from analysis
- File selection prioritizes the largest source code files for representative sampling
