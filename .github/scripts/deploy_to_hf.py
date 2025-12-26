#!/usr/bin/env python3
"""Deploy application to Hugging Face Space."""
import os
import sys

from huggingface_hub import HfApi, login


def main():
    """Deploy to HF Space."""
    repo_id = sys.argv[1] if len(sys.argv) > 1 else "ASI-Engineer/oc_p5-dev"
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("ERROR: HF_TOKEN not configured in GitHub secrets")
        sys.exit(1)

    print(f"Deploying to HF Space: {repo_id}")

    login(hf_token)
    api = HfApi()

    # Create space if it doesn't exist
    try:
        api.repo_info(repo_id=repo_id, repo_type="space")
        print(f"Space {repo_id} already exists")
    except Exception:
        print(f"Creating new space: {repo_id}")
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
        )

    api.upload_folder(
        repo_id=repo_id,
        folder_path=".",
        repo_type="space",
        ignore_patterns=[
            ".git/**",
            ".github/**",
            ".venv/**",
            ".pytest_cache/**",
            ".vscode/**",
            "mlruns/**",
            "mlflow.db*",
            "mlflow_ui.log",
            "ml_model/**",
            "tests/**",
            "scripts/**",
            "docs/**",
            "examples/**",
            "data/**",
            "*.pyc",
            "__pycache__/**",
            "poetry.lock",
            "pyproject.toml",
        ],
    )

    print("Deployment successful")


if __name__ == "__main__":
    main()
