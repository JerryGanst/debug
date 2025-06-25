from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    domain_name: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# 创建 Settings 实例
settings = Settings()
