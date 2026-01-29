import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "database": os.getenv("DB_NAME", "enps"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

# LiteLLM configuration
LITELLM_CONFIG = {
    "api_key": os.getenv("LITELLM_API_KEY", ""),
    "model_name": os.getenv("LITELLM_MODEL_NAME", "openai-gpt-5-mini"),
    "base_url": os.getenv("LITELLM_BASE_URL", "https://litellm.poryadok.ru")
}

# Bitrix24 configuration
BITRIX_TOKEN = os.getenv("BITRIX_TOKEN", "")
BITRIX_USER_ID = int(os.getenv("BITRIX_USER_ID", 0))
BITRIX_ENPS_REPORTS_FOLDER_ID = int(os.getenv("BITRIX_ENPS_REPORTS_FOLDER_ID", 0))

# Paths
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output_reports"))
OUTPUT_DIR.mkdir(exist_ok=True)

# Poradock logging
PORADOCK_TOKEN = os.getenv("PORADOCK_TOKEN", "")