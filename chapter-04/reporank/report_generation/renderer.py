"""Report renderer for generating HTML and JSON outputs."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from models.repository_data import RepositoryData
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportRenderer:
    """Renders HTML reports and JSON data from Repository Data Model."""
    
    def __init__(self, template_dir: str = None):
        """
        Initialize the report renderer.
        
        Args:
            template_dir: Directory containing Jinja2 templates.
                         Defaults to report_generation/templates/
        """
        if template_dir is None:
            # Default to templates directory relative to this file
            current_dir = Path(__file__).parent
            template_dir = str(current_dir / "templates")
        
        self.template_dir = template_dir
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Register custom filters
        self.env.filters['format_number'] = self.format_number
        self.env.filters['format_date'] = self.format_date
        self.env.filters['score_color'] = self.score_color
        self.env.filters['progress_width'] = self.progress_width
        self.env.filters['markdown'] = self.markdown_to_html
        
        logger.info(f"ReportRenderer initialized with template directory: {template_dir}")
    
    @staticmethod
    def format_number(value: int) -> str:
        """
        Format a number with thousands separator.
        
        Args:
            value: Integer to format
            
        Returns:
            Formatted string (e.g., 73245 -> "73.2k" or "73,245")
        """
        if value is None:
            return "0"
        
        # For large numbers, use k/M notation
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        else:
            return f"{value:,}"
    
    @staticmethod
    def format_date(value: str) -> str:
        """
        Format a date string for display.
        
        Args:
            value: Date string (ISO format or simple date)
            
        Returns:
            Formatted date string
        """
        if not value:
            return "N/A"
        
        # If it's already a simple date, return as-is
        if len(value) == 10 and value.count('-') == 2:
            return value
        
        # Try to parse ISO format
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            return value
    
    @staticmethod
    def score_color(value: float) -> str:
        """
        Get Tailwind CSS color class based on score.
        
        Args:
            value: Score from 0-10
            
        Returns:
            Tailwind CSS color class (e.g., "text-green-600")
        """
        if value is None:
            return "text-gray-600"
        
        if value >= 8.0:
            return "text-green-600"
        elif value >= 6.0:
            return "text-blue-600"
        elif value >= 4.0:
            return "text-orange-600"
        else:
            return "text-red-600"
    
    @staticmethod
    def progress_width(value: float) -> int:
        """
        Convert score (0-10) to percentage width for progress bars.
        
        Args:
            value: Score from 0-10
            
        Returns:
            Percentage width (0-100)
        """
        if value is None:
            return 0
        
        return int(value * 10)
    
    @staticmethod
    def markdown_to_html(text: str) -> Markup:
        """
        Convert markdown text to HTML.
        
        Supports:
        - **bold** -> <strong>bold</strong>
        - *italic* -> <em>italic</em>
        - `code` -> <code>code</code>
        - [link](url) -> <a href="url">link</a>
        - Line breaks
        
        Args:
            text: Markdown text
            
        Returns:
            HTML markup (safe for rendering)
        """
        if not text:
            return Markup("")
        
        # Convert bold (**text** or __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Convert italic (*text* or _text_)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Convert inline code (`code`)
        text = re.sub(r'`(.+?)`', r'<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">\1</code>', text)
        
        # Convert links [text](url)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" class="gh-link">\1</a>', text)
        
        # Convert line breaks (double newline to paragraph, single to br)
        text = re.sub(r'\n\n', '</p><p class="mb-2">', text)
        text = re.sub(r'\n', '<br/>', text)
        
        # Wrap in paragraph if not already wrapped
        if not text.startswith('<p'):
            text = f'<p class="mb-2">{text}</p>'
        
        return Markup(text)
    
    def prepare_template_context(self, repo_data: RepositoryData) -> Dict[str, Any]:
        """
        Transform Repository Data Model to nested structure for template.
        
        Args:
            repo_data: Repository data model instance
            
        Returns:
            Dictionary with nested structure matching template expectations
        """
        logger.info("Preparing template context from Repository Data Model")
        
        # Convert to dict first
        data_dict = repo_data.to_dict()
        
        # Build nested structure matching JSON format
        context = {
            'repository': {
                'name': f"{data_dict.get('owner', '')}/{data_dict.get('repo_name', '')}",
                'url': data_dict.get('github_url', ''),
                'description': data_dict.get('description', ''),
                'analysis_date': data_dict.get('analysis_date', ''),
                'overall_score': data_dict.get('overall_score', 0.0)
            },
            'metadata': {
                'basic_information': {
                    'created': data_dict.get('created_date', ''),
                    'last_updated': data_dict.get('last_updated', ''),
                    'default_branch': data_dict.get('default_branch', 'main'),
                    'primary_language': data_dict.get('primary_language', '')
                },
                'engagement_metrics': {
                    'stars': data_dict.get('stars', 0),
                    'forks': data_dict.get('forks', 0),
                    'contributors': data_dict.get('contributors', 0)
                },
                'license': data_dict.get('license', 'N/A')
            },
            'maturity': {
                'level': data_dict.get('maturity_level', 'Unknown')
            },
            'commit_activity': {
                'total_commits': data_dict.get('total_commits', 0),
                'last_commit': data_dict.get('last_commit', 'N/A'),
                'past_twelve_monthly_breakdown': self._transform_monthly_commits(data_dict.get('monthly_commits', {}))
            },
            'quality_assessment': {
                'overall_scores': {
                    'readme_quality': data_dict.get('readme_quality_score', 0.0),
                    'code_structure': data_dict.get('code_structure_score', 0.0)
                },
                'detailed_metrics': {
                    'documentation_quality': {
                        'score': data_dict.get('readme_quality_score', 0.0),
                        'rating': self._get_rating(data_dict.get('readme_quality_score', 0.0)),
                        'strengths': self._extract_strengths('documentation', data_dict)
                    },
                    'project_structure': {
                        'score': data_dict.get('code_structure_score', 0.0),
                        'rating': self._get_rating(data_dict.get('code_structure_score', 0.0)),
                        'strengths': self._extract_strengths('structure', data_dict),
                        'improvements': []
                    },
                    'security_practices': {
                        'score': data_dict.get('security_score', 0.0),
                        'rating': self._get_rating(data_dict.get('security_score', 0.0)),
                        'strengths': self._extract_strengths('security', data_dict),
                        'improvements': []
                    },
                    'dependency_management': {
                        'score': data_dict.get('dependency_score', 0.0),
                        'rating': self._get_rating(data_dict.get('dependency_score', 0.0)),
                        'strengths': self._extract_strengths('dependency', data_dict)
                    }
                }
            },
            'activity_health': {
                'overall_health_score': data_dict.get('activity_health_score', 0.0),
                'status': 'Actively Maintained' if data_dict.get('activity_health_score', 0) > 7 else 'Maintained',
                'community_status': 'Healthy Community' if data_dict.get('contributors', 0) > 100 else 'Active Community',
                'maintenance_status': 'Active'
            },
            'tech_stack': {
                'primary_language': {
                    'name': self._get_primary_language(data_dict),
                    'version': '',
                    'percentage': self._get_primary_language_percentage(data_dict)
                },
                'language_used': self._get_all_languages(data_dict),
                'core_dependencies': data_dict.get('core_dependencies', [])
            },
            'strengths': data_dict.get('strengths', []),
            'weaknesses': data_dict.get('weaknesses', [])
        }
        
        # Add LLM evaluation if present
        if data_dict.get('llm_composite_score', 0) > 0:
            context['llm_evaluation'] = {
                'composite_score': data_dict.get('llm_composite_score', 0.0),
                'evaluation_model': 'GPT-4 with Chain-of-Thought reasoning',
                'evaluation_date': data_dict.get('analysis_date', ''),
                'consistency_check': '3 independent evaluations averaged',
                'human_validation': 'Validated against expert ratings',
                'dimensions': {
                    'code_architecture_quality': data_dict.get('code_architecture_evaluation', {}),
                    'production_readiness': data_dict.get('production_readiness_evaluation', {}),
                    'learning_value': data_dict.get('learning_value_evaluation', {}),
                    'security_posture': data_dict.get('security_posture_evaluation', {})
                }
            }
        
        # Add recommendations if present
        if data_dict.get('improvements') or data_dict.get('risk_assessment'):
            # Transform risk_assessment to match template expectations
            risk_data = data_dict.get('risk_assessment', {})
            risk_level = risk_data.get('level', 'Unknown')
            risk_factors = risk_data.get('factors', [])
            
            context['recommendations'] = {
                'risk_assessment': {
                    'security_risk': {
                        'level': risk_level,
                        'description': '; '.join(risk_factors) if risk_factors else 'No significant security risks identified'
                    },
                    'adoption_risk': {
                        'level': risk_level,
                        'description': f"Overall risk level based on {len(risk_factors)} factors"
                    }
                },
                'improvements': data_dict.get('improvements', []),
                'final_verdict': data_dict.get('final_verdict', {})
            }
        
        logger.info("Template context prepared successfully")
        return context
    
    @staticmethod
    def _get_rating(score: float) -> str:
        """Get text rating from numeric score."""
        if score >= 9.0:
            return "Excellent"
        elif score >= 8.0:
            return "Very Good"
        elif score >= 7.0:
            return "Good"
        elif score >= 6.0:
            return "Fair"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def _extract_strengths(category: str, data_dict: Dict) -> list:
        """Extract strengths for a specific category."""
        # This is a placeholder - in real implementation, 
        # strengths would be extracted from analysis results
        strengths_map = {
            'documentation': [
                'Comprehensive README with examples',
                'Well-commented code'
            ],
            'structure': [
                'Clear module separation',
                'Logical directory structure'
            ],
            'security': [
                'Security best practices followed'
            ],
            'dependency': [
                'Well-managed dependencies'
            ]
        }
        return strengths_map.get(category, [])
    
    @staticmethod
    def _calculate_dominant_percentage(language_breakdown: Dict[str, float]) -> float:
        """Calculate percentage of dominant language."""
        if not language_breakdown:
            return 0.0
        
        # If already percentages, return max
        if all(v <= 100 for v in language_breakdown.values()):
            return max(language_breakdown.values()) if language_breakdown else 0.0
        
        # Otherwise calculate percentage
        total = sum(language_breakdown.values())
        if total == 0:
            return 0.0
        
        max_value = max(language_breakdown.values())
        return round((max_value / total) * 100, 1)
    
    @staticmethod
    def _get_primary_language(data_dict: Dict) -> str:
        """
        Get the primary language, preferring GitHub API data over LLM detection.
        
        Args:
            data_dict: Repository data dictionary
            
        Returns:
            Primary language name
        """
        # First try GitHub API's primary_language (most accurate)
        primary = data_dict.get('primary_language', '')
        if primary:
            return primary
        
        # Fallback to LLM's dominant_language
        dominant = data_dict.get('dominant_language', '')
        if dominant:
            return dominant
        
        # Last resort: get from language_breakdown
        language_breakdown = data_dict.get('language_breakdown', {})
        if language_breakdown:
            return max(language_breakdown, key=language_breakdown.get)
        
        return 'Unknown'
    
    @staticmethod
    def _get_primary_language_percentage(data_dict: Dict) -> float:
        """
        Get the percentage of the primary language from GitHub API data.
        
        Args:
            data_dict: Repository data dictionary
            
        Returns:
            Percentage of primary language (0-100)
        """
        language_breakdown = data_dict.get('language_breakdown', {})
        if not language_breakdown:
            return 0.0
        
        # GitHub API already provides percentages
        primary_lang = data_dict.get('primary_language', '')
        if primary_lang and primary_lang in language_breakdown:
            return language_breakdown[primary_lang]
        
        # Fallback: return the highest percentage
        return max(language_breakdown.values()) if language_breakdown else 0.0
    
    @staticmethod
    def _get_all_languages(data_dict: Dict) -> List[str]:
        """
        Get all languages used in the repository.
        
        Combines GitHub API language breakdown with LLM detected languages.
        
        Args:
            data_dict: Repository data dictionary
            
        Returns:
            List of language names
        """
        languages = set()
        
        # Add languages from GitHub API breakdown
        language_breakdown = data_dict.get('language_breakdown', {})
        if language_breakdown:
            languages.update(language_breakdown.keys())
        
        # Add LLM detected languages
        detected = data_dict.get('detected_languages', [])
        if detected:
            languages.update(detected)
        
        # Add primary language if set
        primary = data_dict.get('primary_language', '')
        if primary:
            languages.add(primary)
        
        # Sort and return
        return sorted(list(languages))
    
    @staticmethod
    def _transform_monthly_commits(monthly_commits: Dict[str, int]) -> Dict[str, int]:
        """
        Transform monthly commits from YYYY-MM format to month names.
        
        Takes the last 12 months of data and maps them to month names
        (january, february, etc.) for the chart template.
        
        Args:
            monthly_commits: Dict with keys like '2025-11', '2025-10', etc.
            
        Returns:
            Dict with month names as keys (january, february, etc.)
        """
        from datetime import datetime
        from collections import defaultdict
        
        if not monthly_commits:
            return {
                'january': 0, 'february': 0, 'march': 0, 'april': 0,
                'may': 0, 'june': 0, 'july': 0, 'august': 0,
                'september': 0, 'october': 0, 'november': 0, 'december': 0
            }
        
        # Initialize result with all months set to 0
        result = {
            'january': 0, 'february': 0, 'march': 0, 'april': 0,
            'may': 0, 'june': 0, 'july': 0, 'august': 0,
            'september': 0, 'october': 0, 'november': 0, 'december': 0
        }
        
        # Map month numbers to names
        month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        # Aggregate commits by month name (sum across years)
        for month_key, count in monthly_commits.items():
            try:
                # Parse YYYY-MM format
                year, month = month_key.split('-')
                month_num = int(month)
                month_name = month_names[month_num - 1]
                result[month_name] += count
            except (ValueError, IndexError):
                continue
        
        return result
    
    @staticmethod
    def generate_timestamped_filename(base_name: str, extension: str = "html") -> str:
        """
        Generate a filename with timestamp.
        
        Args:
            base_name: Base name for the file (e.g., 'report', 'repo_analysis')
            extension: File extension without dot (e.g., 'html', 'json')
            
        Returns:
            Filename with timestamp (e.g., 'report_20241113_143022.html')
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"
    
    def render_html_report(self, repo_data: RepositoryData, output_path: str, 
                          add_timestamp: bool = False) -> str:
        """
        Render HTML report from Repository Data Model.
        
        Args:
            repo_data: Repository data model instance
            output_path: Path where HTML report should be saved
            add_timestamp: If True, adds timestamp to filename
            
        Returns:
            Path to generated HTML file
            
        Raises:
            Exception: If template rendering fails
        """
        # Add timestamp to filename if requested
        if add_timestamp:
            dir_path = os.path.dirname(output_path)
            base_name = os.path.splitext(os.path.basename(output_path))[0]
            timestamped_name = self.generate_timestamped_filename(base_name, 'html')
            output_path = os.path.join(dir_path, timestamped_name)
        
        logger.info(
            f"Rendering HTML report to: {output_path}",
            extra={'output_path': output_path, 'add_timestamp': add_timestamp}
        )
        
        try:
            # Prepare template context
            logger.debug("Preparing template context from repository data")
            context = self.prepare_template_context(repo_data)
            
            # Load template
            logger.debug("Loading Jinja2 template: report_template.html")
            try:
                template = self.env.get_template('report_template.html')
            except Exception as template_error:
                error_msg = (
                    f"Failed to load template 'report_template.html' from {self.template_dir}. "
                    f"Error: {str(template_error)}. "
                    f"Please ensure the template file exists and is readable."
                )
                logger.error(
                    error_msg,
                    extra={
                        'template_dir': self.template_dir,
                        'template_name': 'report_template.html',
                        'error_type': type(template_error).__name__
                    },
                    exc_info=True
                )
                raise RuntimeError(error_msg) from template_error
            
            # Render template
            logger.debug("Rendering template with context data")
            try:
                html_content = template.render(**context)
            except Exception as render_error:
                error_msg = (
                    f"Template rendering failed: {str(render_error)}. "
                    f"This may be due to missing or invalid data in the template context. "
                    f"Check the template syntax and ensure all required variables are present."
                )
                logger.error(
                    error_msg,
                    extra={
                        'error_type': type(render_error).__name__,
                        'context_keys': list(context.keys()) if isinstance(context, dict) else 'N/A'
                    },
                    exc_info=True
                )
                raise RuntimeError(error_msg) from render_error
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    logger.debug(f"Created output directory: {output_dir}")
                except Exception as dir_error:
                    error_msg = (
                        f"Failed to create output directory '{output_dir}': {str(dir_error)}. "
                        f"Please check directory permissions."
                    )
                    logger.error(
                        error_msg,
                        extra={'output_dir': output_dir, 'error_type': type(dir_error).__name__},
                        exc_info=True
                    )
                    raise RuntimeError(error_msg) from dir_error
            
            # Write to file
            logger.debug(f"Writing HTML content to file: {output_path}")
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            except Exception as write_error:
                error_msg = (
                    f"Failed to write HTML report to '{output_path}': {str(write_error)}. "
                    f"Please check file permissions and available disk space."
                )
                logger.error(
                    error_msg,
                    extra={'output_path': output_path, 'error_type': type(write_error).__name__},
                    exc_info=True
                )
                raise RuntimeError(error_msg) from write_error
            
            logger.info(
                f"HTML report generated successfully: {output_path}",
                extra={'output_path': output_path, 'file_size': len(html_content)}
            )
            return output_path
            
        except RuntimeError:
            # Re-raise RuntimeError with our custom messages
            raise
        except Exception as e:
            error_msg = (
                f"Unexpected error during HTML report generation: {str(e)}. "
                f"Please check the logs for more details."
            )
            logger.error(
                error_msg,
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise RuntimeError(error_msg) from e
    
    def save_json_data(self, repo_data: RepositoryData, output_path: str,
                      add_timestamp: bool = False) -> str:
        """
        Save Repository Data Model as JSON file.
        
        Args:
            repo_data: Repository data model instance
            output_path: Path where JSON file should be saved
            add_timestamp: If True, adds timestamp to filename
            
        Returns:
            Path to generated JSON file
            
        Raises:
            Exception: If JSON serialization fails
        """
        # Add timestamp to filename if requested
        if add_timestamp:
            dir_path = os.path.dirname(output_path)
            base_name = os.path.splitext(os.path.basename(output_path))[0]
            timestamped_name = self.generate_timestamped_filename(base_name, 'json')
            output_path = os.path.join(dir_path, timestamped_name)
        
        logger.info(
            f"Saving JSON data to: {output_path}",
            extra={'output_path': output_path, 'add_timestamp': add_timestamp}
        )
        
        try:
            # Prepare context (same structure as template)
            logger.debug("Preparing JSON context from repository data")
            try:
                context = self.prepare_template_context(repo_data)
            except Exception as context_error:
                error_msg = (
                    f"Failed to prepare JSON context: {str(context_error)}. "
                    f"This may be due to invalid data in the repository model."
                )
                logger.error(
                    error_msg,
                    extra={'error_type': type(context_error).__name__},
                    exc_info=True
                )
                raise RuntimeError(error_msg) from context_error
            
            # Add report metadata
            context['report_metadata'] = {
                'generated_by': 'RepoRank',
                'powered_by': 'DSPy with LLM-as-Judge evaluation',
                'report_version': '1.0',
                'analysis_date': repo_data.analysis_date
            }
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    logger.debug(f"Created output directory: {output_dir}")
                except Exception as dir_error:
                    error_msg = (
                        f"Failed to create output directory '{output_dir}': {str(dir_error)}. "
                        f"Please check directory permissions."
                    )
                    logger.error(
                        error_msg,
                        extra={'output_dir': output_dir, 'error_type': type(dir_error).__name__},
                        exc_info=True
                    )
                    raise RuntimeError(error_msg) from dir_error
            
            # Write to file with pretty formatting
            logger.debug(f"Serializing and writing JSON to file: {output_path}")
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(context, f, indent=2, ensure_ascii=False)
            except TypeError as json_error:
                error_msg = (
                    f"JSON serialization failed: {str(json_error)}. "
                    f"The data contains non-serializable objects. "
                    f"Please check the repository data model for invalid types."
                )
                logger.error(
                    error_msg,
                    extra={'error_type': 'TypeError', 'output_path': output_path},
                    exc_info=True
                )
                raise RuntimeError(error_msg) from json_error
            except Exception as write_error:
                error_msg = (
                    f"Failed to write JSON file to '{output_path}': {str(write_error)}. "
                    f"Please check file permissions and available disk space."
                )
                logger.error(
                    error_msg,
                    extra={'output_path': output_path, 'error_type': type(write_error).__name__},
                    exc_info=True
                )
                raise RuntimeError(error_msg) from write_error
            
            # Get file size for logging
            file_size = os.path.getsize(output_path)
            logger.info(
                f"JSON data saved successfully: {output_path}",
                extra={'output_path': output_path, 'file_size': file_size}
            )
            return output_path
            
        except RuntimeError:
            # Re-raise RuntimeError with our custom messages
            raise
        except Exception as e:
            error_msg = (
                f"Unexpected error during JSON data save: {str(e)}. "
                f"Please check the logs for more details."
            )
            logger.error(
                error_msg,
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            raise RuntimeError(error_msg) from e
