import random

# sample DSPy Module imported as a hint on how to organize your code
from data_analysis.dspy_modules import LanguageDetection

# AS PART OF CAPSTONE PROJECT YOU ARE EXPECTED TO IMPLEMENT THE DSPy SIGNATURES AND MODULES
# IN dspy_modules.py and then implement the same in the functions below.
# YOU CAN PRINT THE JSON populated with repo_data.to_json_structure()
# THESE ANALYSIS ARE PLACEHOLDERS FOR YOU TO DELETE AND IMPLEMENT

def analyze_repository_score(repo_data):
    """Populate overall_score and maturity_level in repository section."""
    repo_data.overall_score = round(random.uniform(3.0, 9.5), 1)
    
    maturity_levels = ['Early Stage', 'Growing', 'Stable', 'Mature', 'Legacy']
    repo_data.maturity_level = random.choice(maturity_levels)
    return repo_data


def analyze_quality_metrics(repo_data):
    """Populate quality_metrics scores."""
    repo_data.readme_quality_score = round(random.uniform(3.0, 10.0), 1)
    repo_data.code_structure_score = round(random.uniform(3.0, 10.0), 1)
    repo_data.security_score = round(random.uniform(3.0, 10.0), 1)
    repo_data.dependency_score = round(random.uniform(3.0, 10.0), 1)
    repo_data.activity_health_score = round(random.uniform(3.0, 10.0), 1)
    return repo_data


def analyze_llm_evaluation(repo_data):
    """Populate llm_evaluation section with composite_score and detailed evaluations."""
    repo_data.llm_composite_score = round(random.uniform(3.0, 9.5), 1)
    
    repo_data.code_architecture_evaluation = {
        'score': round(random.uniform(3.0, 10.0), 1),
        'rating': random.choice(['Poor', 'Needs Improvement', 'Good', 'Very Good', 'Excellent']),
        'reasoning': 'Architecture demonstrates clear separation of concerns with modular design patterns.'
    }
    
    repo_data.production_readiness_evaluation = {
        'score': round(random.uniform(3.0, 10.0), 1),
        'rating': random.choice(['Poor', 'Needs Improvement', 'Good', 'Very Good', 'Excellent']),
        'reasoning': 'Project shows good test coverage and deployment practices for production use.'
    }
    
    repo_data.learning_value_evaluation = {
        'score': round(random.uniform(3.0, 10.0), 1),
        'rating': random.choice(['Poor', 'Needs Improvement', 'Good', 'Very Good', 'Excellent']),
        'reasoning': 'Well-documented codebase with clear examples makes it valuable for learning.'
    }
    
    repo_data.security_posture_evaluation = {
        'score': round(random.uniform(3.0, 10.0), 1),
        'rating': random.choice(['Poor', 'Needs Improvement', 'Good', 'Very Good', 'Excellent']),
        'reasoning': 'Security best practices are followed with regular dependency updates and vulnerability scanning.'
    }
    return repo_data



def analyze_recommendations(repo_data):
    """Populate recommendations section with strengths, weaknesses, improvements, risk_assessment, and final_verdict."""
    readme_score = repo_data.readme_quality_score
    code_score = repo_data.code_structure_score
    security_score = repo_data.security_score
    activity_score = repo_data.activity_health_score
    
    repo_data.strengths = []
    if readme_score >= 7.0:
        repo_data.strengths.append(f'Excellent readme quality (score: {readme_score})')
    if code_score >= 7.0:
        repo_data.strengths.append(f'Good code structure (score: {code_score})')
    if security_score >= 7.0:
        repo_data.strengths.append(f'Strong security practices (score: {security_score})')
    if activity_score >= 7.0:
        repo_data.strengths.append(f'Excellent activity health (score: {activity_score})')
    
    if repo_data.stars > 50000:
        repo_data.strengths.append('Strong community engagement (50k+ stars)')
    
    repo_data.weaknesses = []
    if readme_score < 5.0:
        repo_data.weaknesses.append(f'Poor documentation quality (score: {readme_score})')
    if code_score < 5.0:
        repo_data.weaknesses.append(f'Weak code structure (score: {code_score})')
    if security_score < 5.0:
        repo_data.weaknesses.append(f'Security concerns (score: {security_score})')
    if activity_score < 5.0:
        repo_data.weaknesses.append(f'Low activity health (score: {activity_score})')
    
    repo_data.improvements = [
        {'title': 'Increase test coverage', 'description': 'Improve reliability through comprehensive testing'},
        {'title': 'Add code documentation', 'description': 'Add more inline code documentation and examples'},
        {'title': 'Security scanning', 'description': 'Implement automated security scanning'},
        {'title': 'Contribution guidelines', 'description': 'Establish clear contribution guidelines'}
    ]
    
    repo_data.risk_assessment = {
        'security_risk': {
            'level': 'Low' if security_score >= 6.0 else 'Medium' if security_score >= 4.0 else 'High',
            'description': 'Security risk assessment based on code quality and dependency management.'
        },
        'adoption_risk': {
            'level': 'Low' if activity_score >= 6.0 else 'Medium' if activity_score >= 4.0 else 'High',
            'description': 'Adoption risk based on project maintenance status and community support.'
        }
    }
    
    composite_score = repo_data.llm_composite_score
    if composite_score >= 7.0:
        verdict = 'Excellent'
        summary = 'This repository demonstrates high quality across multiple dimensions and is recommended for adoption.'
    elif composite_score >= 5.0:
        verdict = 'Good'
        summary = 'This repository shows solid quality with some areas for improvement.'
    else:
        verdict = 'Poor'
        summary = 'This repository has quality concerns and requires improvement before adoption.'
    
    repo_data.final_verdict = {
        'verdict': verdict,
        'summary': summary,
        'overall_score': composite_score
    }
    return repo_data


def execute(repo_data):
    """Execute all analysis functions to populate repo_data."""
    repo_data = analyze_repository_score(repo_data)
    repo_data = analyze_quality_metrics(repo_data)
    repo_data = analyze_llm_evaluation(repo_data)
    repo_data = analyze_recommendations(repo_data)
    return repo_data
