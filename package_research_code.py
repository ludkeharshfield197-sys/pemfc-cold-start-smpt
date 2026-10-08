"""Build the function-based public research packages."""
from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    run_path(str(Path(__file__).with_name("prepare_github_publication.py")), run_name="__main__")
