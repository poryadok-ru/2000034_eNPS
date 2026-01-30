import os
from pathlib import Path

# Database configuration - используем те же имена переменных что в NPS проекте
DB_CONFIG = {
    "host": os.getenv("DB_HOST", os.getenv("NPS_DB_HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", os.getenv("NPS_DB_PORT", 5433))),
    "database": os.getenv("DB_NAME", os.getenv("NPS_DB_NAME", "enps")),
    "user": os.getenv("DB_USER", os.getenv("NPS_DB_USER", "postgres")),
    "password": os.getenv("DB_PASSWORD", os.getenv("NPS_DB_PASSWORD", "por_pas_123"))
}

# LiteLLM configuration
LITELLM_CONFIG = {
    "api_key": os.getenv("LITELLM_API_KEY", ""),
    "model_name": os.getenv("LITELLM_MODEL_NAME", "openai-gpt-5-mini"),
    "base_url": os.getenv("LITELLM_BASE_URL", "https://litellm.poryadok.ru")
}

# Bitrix24 configuration
BITRIX_TOKEN = os.getenv("BITRIX_TOKEN", "")
BITRIX_USER_ID = int(os.getenv("BITRIX_USER_ID", 163472))
BITRIX_ENPS_REPORTS_FOLDER_ID = int(os.getenv("BITRIX_ENPS_REPORTS_FOLDER_ID", 5057340))

# Paths
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", "/usr/local/bin/wkhtmltopdf")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/output_reports"))
OUTPUT_DIR.mkdir(exist_ok=True)

# Poradock logging
PORADOCK_TOKEN = os.getenv("PORADOCK_TOKEN", os.getenv("PORADOCK_LOG_TOKEN", ""))