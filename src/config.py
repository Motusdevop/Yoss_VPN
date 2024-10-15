from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):

    bot_token: SecretStr
    admin: int
    phone_number: str
    server_password: SecretStr
    pay_url: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()