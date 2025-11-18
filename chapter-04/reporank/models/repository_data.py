"""Repository Data Model - Central data structure for repository information."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class RepositoryData:
    """
    Central data structure that holds all repository information throughout the pipeline.
    """
    
    # Input
    github_url: str = ""
    owner: str = ""
    repo_name: str = ""
    
    # Metadata (from GitHub API)
    description: str = ""
    created_date: str = ""
    last_updated: str = ""
    default_branch: str = "main"
    primary_language: str = ""
    stars: int = 0
    forks: int = 0
    contributors: int = 0
    license: str = ""
    
    # Commit Activity (from GitHub API)
    total_commits: int = 0
    last_commit: str = ""
    monthly_commits: Dict[str, int] = field(default_factory=dict)
    
    # Tech Stack (from local analysis)
    file_extension_counts: Dict[str, int] = field(default_factory=dict)
    detected_languages: List[str] = field(default_factory=list)
    dominant_language: str = ""
    language_breakdown: Dict[str, float] = field(default_factory=dict)
    core_dependencies: List[Dict[str, str]] = field(default_factory=list)
    
    # Code samples for analysis (4-5 largest files)
    analyzed_files: List[str] = field(default_factory=list)
    code_samples: Dict[str, str] = field(default_factory=dict)
    
    # Quality Assessment (programmatic metrics)
    readme_quality_score: float = 0.0
    code_structure_score: float = 0.0
    security_score: float = 0.0
    dependency_score: float = 0.0
    activity_health_score: float = 0.0
    
    # LLM Evaluation (DSPy generated)
    llm_composite_score: float = 0.0
    code_architecture_evaluation: Dict[str, Any] = field(default_factory=dict)
    production_readiness_evaluation: Dict[str, Any] = field(default_factory=dict)
    learning_value_evaluation: Dict[str, Any] = field(default_factory=dict)
    security_posture_evaluation: Dict[str, Any] = field(default_factory=dict)
    
    # Recommendations
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvements: List[Dict[str, str]] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    final_verdict: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    overall_score: float = 0.0
    maturity_level: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json_structure(self) -> Dict:
        """
        Convert to the specific JSON structure expected by the template.
        Transforms flat structure to nested structure matching repo_analysis_data.json.
        """
        return {
            "repository": {
                "name": self.repo_name,
                "url": self.github_url,
                "owner": self.owner,
                "description": self.description,
                "overall_score": self.overall_score,
                "maturity_level": self.maturity_level
            },
            "metadata": {
                "stars": self.stars,
                "forks": self.forks,
                "contributors": self.contributors,
                "created_date": self.created_date,
                "last_updated": self.last_updated,
                "license": self.license,
                "primary_language": self.primary_language,
                "default_branch": self.default_branch
            },
            "commit_activity": {
                "total_commits": self.total_commits,
                "last_commit": self.last_commit,
                "monthly_commits": self.monthly_commits
            },
            "tech_stack": {
                "file_extension_counts": self.file_extension_counts,
                "detected_languages": self.detected_languages,
                "dominant_language": self.dominant_language,
                "language_breakdown": self.language_breakdown,
                "core_dependencies": self.core_dependencies
            },
            "quality_metrics": {
                "readme_quality_score": self.readme_quality_score,
                "code_structure_score": self.code_structure_score,
                "security_score": self.security_score,
                "dependency_score": self.dependency_score,
                "activity_health_score": self.activity_health_score
            },
            "llm_evaluation": {
                "composite_score": self.llm_composite_score,
                "code_architecture": self.code_architecture_evaluation,
                "production_readiness": self.production_readiness_evaluation,
                "learning_value": self.learning_value_evaluation,
                "security_posture": self.security_posture_evaluation
            },
            "recommendations": {
                "strengths": self.strengths,
                "weaknesses": self.weaknesses,
                "improvements": self.improvements,
                "risk_assessment": self.risk_assessment,
                "final_verdict": self.final_verdict
            },
            "analysis_metadata": {
                "analysis_date": self.analysis_date,
                "analyzed_files": self.analyzed_files
            }
        }
