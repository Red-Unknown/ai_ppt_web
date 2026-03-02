import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Try to find .env in project root
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    print(f"Loading environment from {ENV_FILE}")
    load_dotenv(ENV_FILE)
else:
    print(f"Warning: .env file not found at {ENV_FILE}")

# Ensure project root is in sys.path
# if str(ROOT_DIR) not in sys.path:
#    sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """Check if critical environment variables are set."""
    required_vars = ["DEEPSEEK_API_KEY", "TAVILY_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"\nWarning: Missing environment variables: {', '.join(missing)}")
        print("Some integration tests may fail or be skipped.")
    else:
        print("\nEnvironment check passed: API Keys are present.")

@pytest.fixture(scope="session")
def real_settings():
    """Fixture to provide real settings (not mocked) if needed."""
    from backend.app.core.config import settings
    # Ensure settings are reloaded from env
    return settings
