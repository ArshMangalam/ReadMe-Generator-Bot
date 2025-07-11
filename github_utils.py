import requests
import os
from typing import Optional, Dict, Any

# Load GitHub token if available
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Set up headers for GitHub API
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "ReadMe-Generator-Bot/1.0"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def extract_repo_info(repo_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract repository information from GitHub API
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        Dictionary containing repository information or None if failed
    """
    try:
        # Clean and validate URL
        repo_url = repo_url.strip().rstrip('/')
        
        # Handle different URL formats
        if repo_url.startswith('https://github.com/'):
            parts = repo_url.replace('https://github.com/', '').split('/')
        elif repo_url.startswith('github.com/'):
            parts = repo_url.replace('github.com/', '').split('/')
        else:
            # Try to extract from any format
            parts = repo_url.split('/')
            if len(parts) >= 2:
                parts = parts[-2:]  # Take last two parts
            else:
                print(f"🚨 [ERROR] Invalid repository URL format: {repo_url}")
                return None
        
        if len(parts) < 2:
            print(f"🚨 [ERROR] Could not extract username/repo from: {repo_url}")
            return None
        
        username = parts[0]
        repo_name = parts[1]
        
        # Remove .git suffix if present
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # Construct API URL
        api_url = f"https://api.github.com/repos/{username}/{repo_name}"
        
        print(f"🔍 [INFO] Fetching repository data from: {api_url}")
        
        # Make API request
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 404:
            print(f"🚨 [ERROR] Repository not found: {username}/{repo_name}")
            return None
        elif response.status_code == 403:
            print(f"🚨 [ERROR] API rate limit exceeded or private repository")
            return None
        
        response.raise_for_status()
        repo_data = response.json()
        
        # Extract and structure the data
        extracted_data = {
            "name": repo_data.get("name", "Unknown"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "topics": repo_data.get("topics", []),
            "default_branch": repo_data.get("default_branch", "main"),
            "owner": repo_data.get("owner", {}).get("login", "Unknown"),
            "homepage": repo_data.get("homepage"),
            "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "clone_url": repo_data.get("clone_url"),
            "size": repo_data.get("size", 0)
        }
        
        print(f"✅ [SUCCESS] Repository data extracted for: {username}/{repo_name}")
        return extracted_data
        
    except requests.exceptions.Timeout:
        print(f"🚨 [ERROR] Request timeout while fetching repository data")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🚨 [ERROR] Connection error while fetching repository data")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🚨 [ERROR] Request failed: {e}")
        return None
    except Exception as e:
        print(f"🚨 [ERROR] Unexpected error while extracting repository info: {e}")
        return None