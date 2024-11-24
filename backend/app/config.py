# backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """
    Конфигурация приложения.
    Использует переменные окружения из файла .env
    """

    # Базовые настройки приложения
    APP_NAME: str = "Amazon Product Analyzer"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Версионирование
    VERSION: str = "1.0.0"
    API_VERSION: str = "v1"

    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Настройки OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    # Настройки базы данных
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # Настройки Redis (если понадобится кэширование)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # CORS настройки
    BACKEND_CORS_ORIGINS: List[str] = [
        "chrome-extension://*",  # Для Chrome расширения
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Настройки безопасности
    SECRET_KEY: str = "your-super-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"

    # Лимиты и ограничения
    RATE_LIMIT: int = 100  # запросов в минуту
    MAX_CONNECTIONS: int = 10
    TIMEOUT: int = 60  # секунды

    # Настройки API Amazon
    AMAZON_API_DELAY: float = 1.0  # задержка между запросами
    AMAZON_MAX_RETRIES: int = 3
    AMAZON_TIMEOUT: int = 30

    # Пути к файлам и директориям
    STATIC_DIR: str = "static"
    TEMPLATE_DIR: str = "templates"
    UPLOAD_DIR: str = "uploads"

    # Email настройки (если понадобится)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Настройки кэширования
    CACHE_EXPIRE_TIME: int = 3600  # 1 час
    CACHE_PREFIX: str = "amazon_analyzer:"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    def get_database_args(self) -> dict:
        """
        Получение аргументов для подключения к базе данных
        """
        return {
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT
        }

    def get_redis_args(self) -> dict:
        """
        Получение аргументов для подключения к Redis
        """
        return {
            "url": self.REDIS_URL,
            "max_connections": self.REDIS_MAX_CONNECTIONS
        }

    def get_openai_args(self) -> dict:
        """
        Получение аргументов для OpenAI API
        """
        return {
            "model": self.OPENAI_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE
        }

    def get_cors_origins(self) -> List[str]:
        """
        Получение списка разрешенных CORS origins
        """
        return self.BACKEND_CORS_ORIGINS

    def get_security_settings(self) -> dict:
        """
        Получение настроек безопасности
        """
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Создание и кэширование экземпляра настроек
    """
    return Settings()


# Создаем экземпляр настроек
settings = get_settings()

# Определяем базовые пути
ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / settings.STATIC_DIR
TEMPLATE_DIR = ROOT_DIR / settings.TEMPLATE_DIR
UPLOAD_DIR = ROOT_DIR / settings.UPLOAD_DIR

# Создаем необходимые директории
for directory in [STATIC_DIR, TEMPLATE_DIR, UPLOAD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)