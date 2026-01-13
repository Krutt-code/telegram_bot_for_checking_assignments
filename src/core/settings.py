from typing import Literal, Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    # Redis можно задать либо одной строкой REDIS_URL, либо компонентами ниже.
    redis_url: Optional[str] = None
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_db: Optional[int] = None
    redis_user: Optional[str] = None
    redis_password: Optional[str] = None

    mysql_url: Optional[str]
    mysql_user: Optional[str]
    mysql_password: Optional[str]
    mysql_host: Optional[str]
    mysql_database: Optional[str]
    db_pool_size: Optional[int] = 5
    db_max_overflow: Optional[int] = 10
    db_pool_timeout: Optional[int] = 30

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def actual_database_url(self):
        if self.mysql_url:
            return self.mysql_url
        elif all(
            [self.mysql_user, self.mysql_password, self.mysql_host, self.mysql_database]
        ):
            encoded_user = quote_plus(self.mysql_user)
            encoded_password = quote_plus(self.mysql_password)
            return f"mysql+aiomysql://{encoded_user}:{encoded_password}@{self.mysql_host}/{self.mysql_database}"
        else:
            raise ValueError(
                "MYSQL_URL or all of MYSQL_USER, DB_PASSWORD, MYSQL_HOST, MYSQL_DATABASE must be set."
            )

    @property
    def actual_redis_url(self) -> str:
        """
        Возвращает рабочий REDIS URL.

        Приоритет:
        1) REDIS_URL
        2) компоненты REDIS_HOST/REDIS_PORT/REDIS_DB (+ опционально REDIS_USER/REDIS_PASSWORD)
        """

        # Если задан REDIS_HOST — считаем, что конфигурация раздельная и используем её.
        # Это полезно в docker-compose, где .env может содержать REDIS_URL=...localhost...
        # но внутри контейнера нужно ходить по имени сервиса (redis).
        if self.redis_host is None:
            if self.redis_url:
                return self.redis_url
            raise ValueError("REDIS_URL or REDIS_HOST must be set.")

        port = 6379 if self.redis_port is None else self.redis_port
        db = 0 if self.redis_db is None else self.redis_db

        # user/pass могут быть пустыми
        user = None if not self.redis_user else quote_plus(self.redis_user)
        password = None if not self.redis_password else quote_plus(self.redis_password)

        auth = ""
        if user and password:
            auth = f"{user}:{password}@"
        elif password and not user:
            # redis://:password@host
            auth = f":{password}@"
        elif user and not password:
            # редкий случай, но поддержим
            auth = f"{user}@"

        return f"redis://{auth}{self.redis_host}:{port}/{db}"


settings = Settings()
