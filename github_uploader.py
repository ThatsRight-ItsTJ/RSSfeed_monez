from github import Github, GithubException
import logging
import base64

def upload_to_github(github_token: str, repo_name: str, filename: str, content: str) -> None:
    """Upload content to GitHub repository."""
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        try:
            # Try to get existing file
            contents = repo.get_contents(filename)
            # Handle case where contents might be a list
            if isinstance(contents, list):
                file = contents[0] if contents else None
            else:
                file = contents
                
            if file and hasattr(file, 'sha'):
                # Update existing file
                repo.update_file(
                    path=filename,
                    message=f"Update {filename}",
                    content=content,
                    sha=file.sha,
                    branch="main"
                )
                logging.info(f"Updated {filename} in GitHub repository")
            else:
                # File doesn't exist or no SHA, create new
                repo.create_file(
                    path=filename,
                    message=f"Create {filename}",
                    content=content,
                    branch="main"
                )
                logging.info(f"Created {filename} in GitHub repository")
        except Exception as e:
            if "404" in str(e):
                # File doesn't exist, create new
                repo.create_file(
                    path=filename,
                    message=f"Create {filename}",
                    content=content,
                    branch="main"
                )
                logging.info(f"Created {filename} in GitHub repository")
            else:
                raise
    except GithubException as e:
        logging.error(f"GitHub API error: {str(e)}")
    except Exception as e:
        logging.error(f"Error uploading to GitHub: {str(e)}")