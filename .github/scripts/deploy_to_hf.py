#!/usr/bin/env python3
"""
Deploy application to Hugging Face Space.

This script uploads the FastAPI application to HuggingFace Spaces
with Docker SDK for production deployment.
"""
import os
import sys

from huggingface_hub import HfApi, login


def main():
    """Deploy to HF Space."""
    # Get repo ID from command line or use default
    repo_id = sys.argv[1] if len(sys.argv) > 1 else "ASI-Engineer/employee-turnover-dev"
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("❌ ERROR: HF_TOKEN not configured in GitHub secrets")
        sys.exit(1)

    print(f"🚀 Deploying to HF Space: {repo_id}")

    # Login to HuggingFace
    login(hf_token)
    api = HfApi()

    # Check if space exists, create if not
    try:
        api.repo_info(repo_id=repo_id, repo_type="space")
        print(f"✅ Space {repo_id} already exists")
    except Exception:
        print(f"📦 Creating new space: {repo_id}")
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
        )

    # Upload application files
    print("📤 Uploading files to HF Space...")

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
            "__pycache__/**",
            "*.pyc",
            ".coverage",
            "htmlcov/**",
            "mlruns/**",
            "mlflow.db*",
            "mlflow_ui.log",
            "ml_model/**",
            "tests/**",
            "examples/**",
            "docs/**",
            "scripts/**",
            ".env",
            ".env.example",
            ".flake8",
            "poetry.lock",
            "pyproject.toml",
            "pytest.ini",
            "README.old.md",
            "test_api.py",
            "main.py",
            "etapes.txt",
            "data/**",
            "logs/**",
        ],
    )

    # Upload README for HF Spaces
    api.upload_file(
        path_or_fileobj="README_HF.md",
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="space",
    )

    print("✅ Deployment successful!")
    print(f"🌐 Space URL: https://huggingface.co/spaces/{repo_id}")


if __name__ == "__main__":
    main()
