from os import getenv
from dotenv import load_dotenv
from pydantic import PostgresDsn, HttpUrl
from pydantic_settings import BaseSettings
from src.core.logger import LOGGING
from logging import config as logging_config

load_dotenv()
logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    project_name: str = getenv("PROJECT_NAME", "Url-shorter")
    project_host: str | HttpUrl = getenv("PROJECT_HOST", "localhost")
    project_port: int = getenv("PROJECT_PORT", "8080")
    project_db: str = getenv("PROJECT_DB", "")
    project_shortener: str = getenv("PROJECT_SHORTENER", "clckru")


app_settings = AppSettings()
