import os

LOG_CONFIG = {
    "formatters": {"bunyan": {"()": "bunyan.BunyanFormatter"}},
    "handlers": {
        "bunyan": {
            "class": "logging.StreamHandler",
            "formatter": "bunyan",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {"level": os.getenv("DEBUG_LEVEL", "INFO"), "handlers": ["bunyan"]},
    "version": 1,
}

DATABASE = {
    "account": os.getenv("SNOW_ACCOUNT", "nzb76949.us-east-1"),
    "user": os.getenv("SNOW_USERNAME", "STREAMLIT"),
    "password": os.getenv("SNOW_PASSWORD", None),
    "private_key": os.getenv("SNOW_PRIVATE_KEY", None),
    "private_key_passphrase": os.getenv("SNOW_PRIVATE_KEY_PASSPHRASE", None),
    "role": os.getenv("SNOW_ROLE", "STREAMLIT"),
    "warehouse": os.getenv("SNOW_WHS", "REPORTING_XS"),
    "database": os.getenv("SNOW_DB", "CRUNCHBASE_BASIC_COMPANY_DATA"),
    "schema": os.getenv("SNOW_SCHEMA", "PUBLIC"),
    "query_tag": os.getenv("SNOW_QUERY_TAG", "SnowAI"),
    "environment": os.getenv("SNOW_ENVIRONMENT", "DEV"),
    "client_session_keep_alive": os.getenv("SNOW_CLIENT_SESSION_KEEP_ALIVE", False),
}

CHATGPT = {
    "api_url": os.getenv("CHATGPT_API_URL", "https://api.openai.com/v1/completions"),
    "api_key": os.getenv("CHATGPT_API_KEY", ""),
    "model": os.getenv("CHATGPT_MODEL", "gpt-3.5-turbo"),
}
