import os
from typing import overload, Optional, Literal
from dotenv import load_dotenv

load_dotenv()

@overload
def get_env_var(var_name: str, unsafe: Literal[False] = False) -> str:
    ...

@overload
def get_env_var(var_name: str, unsafe: Literal[True]) -> Optional[str]:
    ...

def get_env_var(var_name: str, unsafe: bool = False) -> Optional[str]:
    """
    Retrieves an environment variable by name.

    Args:
        var_name: The name of the environment variable.
        unsafe: If True, returns None if the variable is not found.
                If False (default), raises an error.

    Raises:
        ValueError: If the environment variable is not set and unsafe is False.

    Returns:
        str or None: The value of the environment variable, or None if not found and unsafe is True.
    """
    value = os.getenv(var_name)
    if not value:
        if unsafe:
            return None
        else:
            raise ValueError(f"The '{var_name}' environment variable must be set.")
    return value


DB_USER = get_env_var("DB_USER")
DB_PASSWORD = get_env_var("DB_PASSWORD")
DB_HOST = get_env_var("DB_HOST")
DB_PORT = get_env_var("DB_PORT")
DB_NAME = get_env_var("DB_NAME")

MILVUS_HOST = get_env_var("MILVUS_HOST")
MILVUS_PORT = get_env_var("MILVUS_PORT")

TELEGRAM_BOT_API = get_env_var("TELEGRAM_BOT_API")
TELEGRAM_CHAT_IDS = get_env_var("TELEGRAM_CHAT_IDS")

STORAGE_FOLDER = get_env_var("STORAGE_FOLDER")

MILVUS_ADDRESS = f"http://{MILVUS_HOST}:{MILVUS_PORT}"
