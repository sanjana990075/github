import requests
import os
from fastapi import HTTPException

def fetch_github_issue(repo_url: str, issue_number: int) -> str:
    """
    Fetch issue title, body, and comments from GitHub API.
    
    Args:
        repo_url (str): The web URL of the repository (e.g., https://github.com/owner/repo)
        issue_number (int): The issue number.
        
    Returns:
        str: A formatted string containing the issue title, body, and comments.
    """
    # Normalize URL
    clean_url = repo_url.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    parts = clean_url.split("/")
    
    if len(parts) < 3:
        raise ValueError("Invalid GitHub URL. Use format: github.com/owner/repo")

    owner, repo = parts[1], parts[2]

    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    comments_url = f"{issue_url}/comments"

    headers = {
        "User-Agent": "GitHubIssueAnalyzer/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # Fetch issue metadata
        issue_resp = requests.get(issue_url, headers=headers)
        issue_resp.raise_for_status()
        issue = issue_resp.json()

        # Fetch comments
        comments_resp = requests.get(comments_url, headers=headers)
        comments_resp.raise_for_status()
        comments = comments_resp.json()

        # Construct the text payload for the LLM
        text = f"Title: {issue.get('title', '')}\n\n"
        text += f"Body: {issue.get('body', '')}\n\n"
        
        if isinstance(comments, list) and comments:
            text += "--- Comments ---\n"
            for i, c in enumerate(comments, 1):
                body = c.get('body', '').strip()
                if body:
                    text += f"Comment {i}: {body}\n\n"
        else:
            text += "No comments found.\n"
            
        return text

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError("Issue not found. Please check the URL and issue number.")
        elif e.response.status_code == 403:
            raise ValueError("GitHub API rate limit exceeded or access denied.")
        raise e
