import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SpacePoint Portal MVP"
    
    # DB
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Admin
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    
    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "ahmad2012yacine@gmail.com"
    SMTP_PASSWORD: str = "xculshltpnwglfju"
    SMTP_FROM: str = "SpacePoint <ahmad2012yacine@gmail.com>"
    
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

settings = Settings()
