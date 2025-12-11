from typing import Literal, Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    redis_url: str

    mysql_url: Optional[str]
    mysql_user: Optional[str]
    mysql_password: Optional[str]
    mysql_host: Optional[str]
    mysql_database: Optional[str]

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def actual_database_url(self):
        if self.mysql_url:
            return self.mysql_url
        elif all(
            [self.mysql_user, self.mysql_password, self.mysql_host, self.mysql_database]
        ):
            encoded_user = quote_plus(self.mysql_url)
            encoded_password = quote_plus(self.mysql_password)
            return f"mysql+aiomysql://{encoded_user}:{encoded_password}@{self.mysql_host}/{self.mysql_database}"
        else:
            raise ValueError(
                "MYSQL_URL or all of MYSQL_USER, DB_PASSWORD, MYSQL_HOST, MYSQL_DATABASE must be set."
            )


settings = Settings()
