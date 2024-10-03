# core/config.py

import os

from pydantic import BaseModel, field_validator
from pydantic.networks import PostgresDsn

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env")

# Database ENV variables
POSTGRES_ADDRESS = os.getenv("POSTGRES_ADDRESS", "0.0.0.0")
POSTGRES_DB = os.getenv("POSTGRES_DB", "psyco_tests")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", 10))
POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW", 20))

POSTGRES_ECHO = os.getenv("POSTGRES_ECHO", "True").lower() in ('true', '1')

# App ENV variables
DEBUG = os.getenv("DEBUG", "True").lower() in ('true', '1')
APP_RUN_HOST = str(os.getenv("APP_RUN_HOST", "0.0.0.0"))
APP_RUN_PORT = int(os.getenv("APP_RUN_PORT", 8000))

# SQLAdmin ENV variables
SQLADMIN_SECRET_KEY = os.getenv("SQLADMIN_SECRET_KEY", "sqladmin_secret_key")
SQLADMIN_USERNAME = os.getenv("SQLADMIN_USERNAME", "admin")
SQLADMIN_PASSWORD = os.getenv("SQLADMIN_PASSWORD", "password")

# Bot ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_WELCOME_MESSAGE = os.getenv("BOT_WELCOME_MESSAGE", "Hello, {username}, I'm your Psyco-Bot!")

# CORS ENV variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", ["*"])

MEDIA_FILES_ALLOWED_EXTENSIONS = os.getenv("MEDIA_FILES_ALLOWED_EXTENSIONS",
                                           ['.jpg', '.jpeg', '.png'])


class DBConfig(BaseModel):
    url: PostgresDsn = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:5432/{POSTGRES_DB}"
    pool_size: int = POSTGRES_POOL_SIZE
    max_overflow: int = POSTGRES_MAX_OVERFLOW
    echo: bool = POSTGRES_ECHO

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

    @field_validator('pool_size', 'max_overflow')
    def validate_positive_int(cls, v):
        if v <= 0:
            raise ValueError("Must be a positive integer")
        return v


class RunConfig(BaseModel):
    debug: bool = DEBUG
    host: str = APP_RUN_HOST
    port: int = APP_RUN_PORT


class SQLAdminConfig(BaseModel):
    secret_key: str = SQLADMIN_SECRET_KEY
    username: str = SQLADMIN_USERNAME
    password: str = SQLADMIN_PASSWORD


class BotConfig(BaseModel):
    token: str = BOT_TOKEN
    welcome_message: str = BOT_WELCOME_MESSAGE
    user_error_message: str = "Something went wrong. Please try again later."
    admin_error_message: str = ("Извините, произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к разработчику с "
        "подробной информацией: когда и после какого действия произошла ошибка.")
    confirming_words: list[str] = ["да", "yes", "конечно", "отправить", "send", "accept", "absolutely"]


class CORSConfig(BaseModel):
    allowed_origins: list = ALLOWED_ORIGINS


class MediaConfig(BaseModel):
    # base_url: str = "http://localhost:8000"
    base_url: str = "https://6fde-2405-9800-b662-23fa-a44b-d1c3-ec92-818e.ngrok-free.app"
    movie_quiz_path: str = "media/movie_quiz"
    allowed_image_extensions: list[str] = list(MEDIA_FILES_ALLOWED_EXTENSIONS)
    psyco_test_path: str = "media/psyco_tests"

    @field_validator('movie_quiz_path')
    def validate_path(cls, v):
        if not os.path.isabs(v):
            raise ValueError("Path must be absolute")
        return v

    @field_validator('allowed_image_extensions')
    def validate_extensions(cls, v):
        if not all(ext.startswith('.') for ext in v):
            raise ValueError("All extensions must start with a dot")
        return v


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    admin_panel: SQLAdminConfig = SQLAdminConfig()
    db: DBConfig = DBConfig()
    bot: BotConfig = BotConfig()
    cors: CORSConfig = CORSConfig()
    media: MediaConfig = MediaConfig()


settings = Settings()
