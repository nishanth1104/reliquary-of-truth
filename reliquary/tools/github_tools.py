import subprocess
import os
from typing import Dict, Any


def create_github_pr(repo_url: str, branch: str, title: str, body: str, token: str) -> Dict[str, Any]:
    """
    Creates a GitHub Pull Request using PyGithub.

    Args:
        repo_url: Repository URL (e.g., https://github.com/user/repo)
        branch: Branch name to create PR from
        title: PR title
        body: PR description
        token: GitHub personal access token

    Returns:
        Dictionary with PR details (number, html_url, etc.)
    """
    try:
        from github import Github

        # Parse owner and repo from URL
        # Example: https://github.com/owner/repo -> owner, repo
        parts = repo_url.rstrip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')

        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(f"{owner}/{repo_name}")

        # Get default branch (usually main or master)
        default_branch = repo.default_branch

        # Create PR
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base=default_branch
        )

        return {
            "number": pr.number,
            "html_url": pr.html_url,
            "state": pr.state,
            "created_at": pr.created_at.isoformat()
        }

    except ImportError:
        # Fallback to gh CLI if PyGithub not available
        return create_github_pr_cli(repo_url, branch, title, body, token)
    except Exception as e:
        raise RuntimeError(f"Failed to create PR: {str(e)}")


def create_github_pr_cli(repo_url: str, branch: str, title: str, body: str, token: str) -> Dict[str, Any]:
    """
    Creates a GitHub Pull Request using gh CLI.

    Args:
        repo_url: Repository URL
        branch: Branch name
        title: PR title
        body: PR description
        token: GitHub token

    Returns:
        Dictionary with PR details
    """
    try:
        # Set GitHub token
        env = os.environ.copy()
        env['GH_TOKEN'] = token

        # Create PR using gh CLI
        result = subprocess.run(
            ['gh', 'pr', 'create', '--title', title, '--body', body, '--head', branch],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )

        pr_url = result.stdout.strip()

        # Extract PR number from URL
        pr_number = int(pr_url.split('/')[-1]) if pr_url else None

        return {
            "number": pr_number,
            "html_url": pr_url,
            "state": "open",
            "created_at": None
        }

    except Exception as e:
        raise RuntimeError(f"Failed to create PR via CLI: {str(e)}")


def push_to_branch(repo_path: str, branch_name: str, commit_message: str):
    """
    Commits current changes and pushes to specified branch.

    Args:
        repo_path: Path to the repository
        branch_name: Branch to push to
        commit_message: Commit message

    Raises:
        RuntimeError: If git operations fail
    """
    try:
        # Change to repo directory
        original_dir = os.getcwd()
        os.chdir(repo_path)

        # Create and checkout branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)

        # Stage all changes
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)

        # Commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)

        # Push
        subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True, capture_output=True)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}")
    finally:
        os.chdir(original_dir)


def upload_proof_gist(content: bytes, token: str, filename: str = "proof_bundle.zip") -> str:
    """
    Uploads proof bundle to GitHub Gist.

    Args:
        content: File content as bytes
        token: GitHub token
        filename: Filename for the gist

    Returns:
        Gist URL
    """
    try:
        from github import Github
        import base64

        g = Github(token)
        user = g.get_user()

        # GitHub Gists API doesn't support binary files well
        # Instead, we'll create a text gist with base64-encoded content
        encoded_content = base64.b64encode(content).decode('utf-8')

        gist = user.create_gist(
            public=False,
            files={
                filename + ".b64": {
                    "content": encoded_content
                }
            },
            description="Reliquary of Truth - Proof Bundle"
        )

        return gist.html_url

    except Exception as e:
        raise RuntimeError(f"Failed to upload to Gist: {str(e)}")
