import requests

from fastmcp import FastMCP # <2>
from fastmcp.server.auth.providers.github import GitHubProvider # <3>
from fastmcp.server.dependencies import get_access_token # <4>

auth_provider = GitHubProvider( 
    client_id="SAMPLE_CLIENT_ID_ADD_YOURS",
    client_secret="SAMPLE_CLIENT_SECRET_ADD_YOURS",
    base_url="http://localhost:8000",
) # <5>

mcp = FastMCP(name="GitHub Secured App", auth=auth_provider)

@mcp.tool # <6>
async def get_user_info() -> dict:
    """Get the user's GitHub information, details, or profile"""
    token = get_access_token() # <7>
    return {
        "github_user": token.claims.get("login"),
        "name": token.claims.get("name"),
        "email": token.claims.get("email")
    }

@mcp.tool
async def list_starred_repos() -> list[dict]: 
    """List all repositories starred by the authenticated user."""
    token = get_access_token()
    github_token = token.token
    
    response = requests.get(
        "https://api.github.com/user/starred",
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        },
    ) # <8>
    
    response.raise_for_status()
    repos = response.json() # <9>
    
    result = []
    for repo in repos:
        result.append({
            "name": repo["full_name"],
            "description": repo.get("description", "No description"),
            "stars": repo["stargazers_count"],
            "language": repo.get("language", "Unknown"),
            "url": repo["html_url"],
        }) 
    
    return result

if __name__ == "__main__":
    mcp.run(transport="http", port=8000) # <1>
