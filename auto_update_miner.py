import subprocess
import os
import sys
import logging
import importlib
from typing import Optional

# Repository setup
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT_PATH = "neurons/miner.py"
BRANCH = 'main'

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_git_command(command: list[str]) -> Optional[str]:
    """Executes a Git command and returns the output."""
    try:
        result = subprocess.run(
            ['git', '-C', REPO_PATH] + command,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e}")
        return None

def get_local_version() -> Optional[str]:
    """Reads the local version from dml/chain/__init__.py."""
    try:
        sys.path.insert(0, REPO_PATH)
        import dml.chain as chain
        importlib.reload(chain)  
        return getattr(chain, '__spec_version__', None)
    except ImportError:
        logging.error("Failed to import dml.chain module")
        return None
    finally:
        sys.path.pop(0)

def get_remote_version() -> Optional[str]:
    """Fetches the remote version from Git."""
    if run_git_command(['fetch']) is None:
        return None

    remote_content = run_git_command(['show', f'origin/{BRANCH}:dml/chain/__init__.py'])
    if remote_content is None:
        return None

    for line in remote_content.split('\n'):
        if line.startswith('__spec_version__'):
            return line.split('=')[1].strip().strip("'\"")

    logging.error("Could not find __spec_version__ in remote dml/chain/__init__.py")
    return None

def update_repo() -> bool:
    """Performs a Git pull to update the repository."""
    return run_git_command(['pull']) is not None

def install_packages():
    """Installs required dependencies in editable mode."""
    try:
        result = subprocess.run(['pip', 'install', '-e', '.'], check=True, capture_output=True, text=True)
        logging.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Package installation failed: {e.stderr}")

def restart_script():
    """Restarts the script with the updated version."""
    logging.info("Restarting script with updated version...")
    os.execv(sys.executable, ['python'] + sys.argv)

def main():
    try:
        local_version = get_local_version()
        remote_version = get_remote_version()

        if not local_version or not remote_version:
            logging.error("Could not retrieve version info.")
            return 1

        logging.info(f"Local version: {local_version}, Remote version: {remote_version}")

        if int(local_version) != int(remote_version):
            logging.info(f"Updating to latest version from branch {BRANCH}.")
            if not update_repo():
                raise Exception("Failed to update repository.")

            install_packages()
            restart_script()

        logging.info("No updates required, running miner...")
        subprocess.run([sys.executable, MAIN_SCRIPT_PATH], check=True)

    except Exception as e:
        logging.error(f"Update process failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
