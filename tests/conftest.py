import os
import pytest

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(tests_dir)
    
    # Get the current working directory
    cwd = os.getcwd()
    
    # Check if the current working directory is the same as the repo root
    if cwd != repo_root:
        print(f"Please run pytest from the root of the repository: {repo_root}")
        pytest.exit("Exiting pytest because it was not run from the root of the repository.")