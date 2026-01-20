from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """
    Load environment variables from .env file in the backend root directory.

    This function finds the backend directory by traversing up from utils.py
    (which is located at backend/src/aerooffers/utils.py) to backend/.
    """
    # utils.py is at backend/src/aerooffers/utils.py
    # So we go up 3 levels to get to backend/
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path, override=False)
