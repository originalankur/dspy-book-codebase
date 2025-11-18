# Chapter 4: Repository Analysis with RepoRank

This chapter serves as a CAPSTONE project where the reader of the book will implement the missing pieces that will result in creation of a comprehensive repository analysis system using DSPy and GitHub data. 

The `reporank` module analyzes GitHub repositories to extract insights about code quality, structure, and characteristics.

## Project Overview

RepoRank is a tool that:
- Fetches repository metadata from GitHub API
- Clones repositories locally for deep analysis
- Analyzes code structure and file composition ( TO BE IMPLEMENTED BY READER )
- Extracts dependencies across multiple ecosystems 
- Generates detailed reports in JSON and HTML formats

## Environment Setup

### Create a Virtual Environment

It's recommended to create a separate Python environment for RepoRank to avoid dependency conflicts:

```bash
# Create a virtual environment
python -m venv reporank_env

# Activate the environment
# On macOS/Linux:
source reporank_env/bin/activate
```

### Install Dependencies

Once your environment is activated, install the required packages:

```bash
cd chapter-04/reporank
pip install -r requirements.txt
```

The `requirements.txt` file contains all necessary dependencies including:
- `requests` - For GitHub API interactions
- `gitpython` - For repository cloning
- `dspy` - For AI-powered analysis
- And other supporting libraries

## Running the Analysis

### Basic Usage

To analyze a GitHub repository, run:

```bash
python main.py https://github.com/django/django
```

Replace the URL with any public GitHub repository you want to analyze.

### What Happens During Execution

1. **Data Acquisition**: The tool fetches repository metadata from GitHub API
2. **Repository Cloning**: The repository is cloned locally for detailed analysis
3. **Code Analysis**: File structure, extensions, and dependencies are analyzed
4. **Report Generation**: Results are compiled into JSON and HTML reports
5. **Cleanup**: Temporary files are removed

### Output Files

Analysis results are saved in the `output` folder with the following structure:

```
output/
├── repository_name_analysis.json
└── repository_name_analysis.html
```

#### JSON Output (`repository_name_analysis.json`)

Contains structured data about the repository:

```json
{
  "repository": {
    "name": "django/django",
    "url": "django/django",
    "description": "The Web framework for perfectionists with deadlines.",
    "analysis_date": "2025-11-18T12:58:00.149281",
    "overall_score": 8.9
  },
  "metadata": {
    "basic_information": {
      "created": "2012-04-28T02:47:18Z",
      "last_updated": "2025-11-18T07:12:45Z",
      "default_branch": "main",
      "primary_language": "Python"
    },
    "engagement_metrics": {
      "stars": 85825,
      "forks": 33234,
      "contributors": 100
    },
    "license": "BSD 3-Clause \"New\" or \"Revised\" License"
  },
  "maturity": {
    "level": "Stable"
  },
  "commit_activity": {
    "total_commits": 34042,
    "last_commit": "2025-11-18T01:44:42",
    "past_twelve_monthly_breakdown": {
      "january": 139,
      "february": 71,
      "march": 82,
      "april": 70,
      "may": 56,
      "june": 63,
      "july": 66,
      "august": 93,
      "september": 104,
      "october": 85,
      "november": 75,
      "december": 68
    }
  },
  "quality_assessment": {
    "overall_scores": {
      "readme_quality": 4.6,
      "code_structure": 4.3
    },
    "detailed_metrics": {
      "documentation_quality": {
        "score": 4.6,
        "rating": "Needs Improvement",
        "strengths": [
          "Comprehensive README with examples",
          "Well-commented code"
        ]
      },
      "project_structure": {
        "score": 4.3,
        "rating": "Needs Improvement",
        "strengths": [
          "Clear module separation",
          "Logical directory structure"
        ],
        "improvements": []
      },
      "security_practices": {
        "score": 7.2,
        "rating": "Good",
        "strengths": [
          "Security best practices followed"
        ],
        "improvements": []
      },
      "dependency_management": {
        "score": 6.3,
        "rating": "Fair",
        "strengths": [
          "Well-managed dependencies"
        ]
      }
    }
  },
  "activity_health": {
    "overall_health_score": 7.5,
    "status": "Actively Maintained",
    "community_status": "Active Community",
    "maintenance_status": "Active"
  },
  "tech_stack": {
    "primary_language": {
      "name": "Python",
      "version": "",
      "percentage": 97.04
    },
    "language_used": [
      "CSS",
      "JavaScript",
      "Jinja",
      "Procfile",
      "Python",
      "Smarty"
    ],
    "core_dependencies": [
      {
        "name": "eslint",
        "version": "^9.36.0",
        "ecosystem": "Node.js"
      },
      {
        "name": "puppeteer",
        "version": "^24.22.0",
        "ecosystem": "Node.js"
      },
      {
        "name": "grunt",
        "version": "^1.6.1",
        "ecosystem": "Node.js"
      },
      {
        "name": "grunt-cli",
        "version": "^1.5.0",
        "ecosystem": "Node.js"
      },
      {
        "name": "grunt-contrib-qunit",
        "version": "^10.1.1",
        "ecosystem": "Node.js"
      },
      {
        "name": "qunit",
        "version": "^2.24.1",
        "ecosystem": "Node.js"
      }
    ]
  },
  "strengths": [
    "Strong security practices (score: 7.2)",
    "Excellent activity health (score: 7.5)",
    "Strong community engagement (50k+ stars)"
  ],
  "weaknesses": [
    "Poor documentation quality (score: 4.6)",
    "Weak code structure (score: 4.3)"
  ],
  "llm_evaluation": {
    "composite_score": 3.5,
    "evaluation_model": "GPT-4 with Chain-of-Thought reasoning",
    "evaluation_date": "2025-11-18T12:58:00.149281",
    "consistency_check": "3 independent evaluations averaged",
    "human_validation": "Validated against expert ratings",
    "dimensions": {
      "code_architecture_quality": {
        "score": 4.1,
        "rating": "Good",
        "reasoning": "Architecture demonstrates clear separation of concerns with modular design patterns."
      },
      "production_readiness": {
        "score": 3.5,
        "rating": "Good",
        "reasoning": "Project shows good test coverage and deployment practices for production use."
      },
      "learning_value": {
        "score": 9.0,
        "rating": "Very Good",
        "reasoning": "Well-documented codebase with clear examples makes it valuable for learning."
      },
      "security_posture": {
        "score": 7.7,
        "rating": "Very Good",
        "reasoning": "Security best practices are followed with regular dependency updates and vulnerability scanning."
      }
    }
  },
  "recommendations": {
    "risk_assessment": {
      "security_risk": {
        "level": "Unknown",
        "description": "No significant security risks identified"
      },
      "adoption_risk": {
        "level": "Unknown",
        "description": "Overall risk level based on 0 factors"
      }
    },
    "improvements": [
      {
        "title": "Increase test coverage",
        "description": "Improve reliability through comprehensive testing"
      },
      {
        "title": "Add code documentation",
        "description": "Add more inline code documentation and examples"
      },
      {
        "title": "Security scanning",
        "description": "Implement automated security scanning"
      },
      {
        "title": "Contribution guidelines",
        "description": "Establish clear contribution guidelines"
      }
    ],
    "final_verdict": {
      "verdict": "Poor",
      "summary": "This repository has quality concerns and requires improvement before adoption.",
      "overall_score": 3.5
    }
  },
  "report_metadata": {
    "generated_by": "RepoRank",
    "powered_by": "DSPy with LLM-as-Judge evaluation",
    "report_version": "1.0",
    "analysis_date": "2025-11-18T12:58:00.149281"
  }
}
```

#### HTML Output (`repository_name_analysis.html`)

A formatted, interactive report displaying:
- Repository overview and statistics
- Code composition breakdown (file types, languages)
- Dependency analysis with ecosystem information
- Code quality metrics and insights
- Visual charts and graphs
- Recommendations for improvement

## How Data is Acquired

For detailed information about how data is fetched and processed, refer to the [Data Acquisition Module Documentation](./reporank/data_acquisition/README.md).

## Example Workflow

```bash
# 1. Activate environment
source reporank_env/bin/activate

# 2. Run analysis on a repository
python main.py https://github.com/django/django

# 3. Check the output folder
ls -la output/

# 4. Open the HTML report in your browser
open output/django_django_report.html

# 5. Deactivate environment when done
deactivate
```

## Troubleshooting

**Issue**: "GitPython not installed"
- Solution: Ensure you've run `pip install -r requirements.txt` in the activated environment

**Issue**: "GitHub API rate limit exceeded"
- Solution: The module includes exponential backoff. Wait a few minutes and try again, or configure a GitHub token in `config.py`

**Issue**: "Repository clone failed"
- Solution: Verify the repository URL is correct and publicly accessible