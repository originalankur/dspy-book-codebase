#!/usr/bin/env python3
"""Main workflow orchestrator for RepoRank."""

import argparse
import os
import sys
import re
from typing import Tuple

from config import Config
from data_acquisition.github_client import GitHubClient
from data_acquisition.repo_analyzer import RepositoryAnalyzer
from data_acquisition.acquisition_pipeline import AcquisitionPipeline
from data_analysis.analysis_engine import execute as data_analysis_execute
from report_generation.renderer import ReportRenderer
from utils.logger import setup_logger, get_logger


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='RepoRank - Analyze GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('github_url', type=str, help='GitHub repository URL')
    parser.add_argument('-o', '--output', type=str, default='./output', help='Output directory')
    parser.add_argument('-t', '--token', type=str, default=None, help='GitHub API token')
    parser.add_argument('-l', '--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    return parser.parse_args()


def validate_github_url(url: str) -> Tuple[str, str]:
    """Validate and parse GitHub URL."""
    url = url.strip().rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)',
        r'github\.com/([^/]+)/([^/]+)',
        r'^([^/]+)/([^/]+)$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            if owner and repo:
                return owner, repo
    
    raise ValueError(f"Invalid GitHub URL: {url}")


def main() -> int:
    """Main workflow execution."""
    args = parse_arguments()
    logger = setup_logger(name="reporank", log_level=args.log_level)
    
    logger.info("=" * 80)
    logger.info("RepoRank - GitHub Repository Analysis Tool")
    logger.info("=" * 80)
    
    try:
        owner, repo_name = validate_github_url(args.github_url)
        logger.info(f"Analyzing: {owner}/{repo_name}")
    except ValueError as e:
        logger.error(f"URL validation failed: {e}")
        return 1
    
    try:
        config = Config.from_env()
        config.output_dir = args.output
        config.log_level = args.log_level
        if args.token:
            config.github_token = args.token
        
        os.makedirs(config.output_dir, exist_ok=True)
        logger.info(f"Output directory: {config.output_dir}")
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        return 1
    
    try:
        logger.info("Initializing components...")
        github_client = GitHubClient(token=config.github_token)
        repo_analyzer = RepositoryAnalyzer()
        acquisition_pipeline = AcquisitionPipeline(github_client, repo_analyzer)
        report_renderer = ReportRenderer()
        logger.info("Components initialized")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return 1
    
    try:
        logger.info("STAGE 1: DATA ACQUISITION")
        repo_data = acquisition_pipeline.execute(args.github_url)
        logger.info("Data acquisition complete")
    except Exception as e:
        logger.error(f"Data acquisition failed: {e}")
        return 1
    
    try:
        logger.info("STAGE 2: DATA ANALYSIS")
        repo_data = data_analysis_execute(repo_data)
        logger.info("Data analysis complete")
    except Exception as e:
        logger.error(f"Data analysis failed: {e}")
        return 1
    
    try:
        logger.info("STAGE 3: REPORT GENERATION")
        html_path = os.path.join(config.output_dir, f"{owner}_{repo_name}_report.html")
        json_path = os.path.join(config.output_dir, f"{owner}_{repo_name}_data.json")
        
        html_output = report_renderer.render_html_report(repo_data, html_path)
        json_output = report_renderer.save_json_data(repo_data, json_path)
        
        logger.info(f"HTML report: {html_output}")
        logger.info(f"JSON data: {json_output}")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return 1
    
    logger.info("=" * 80)
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"Repository: {owner}/{repo_name}")
    logger.info(f"Overall Score: {repo_data.overall_score}/10")
    logger.info(f"Maturity Level: {repo_data.maturity_level}")
    logger.info("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
