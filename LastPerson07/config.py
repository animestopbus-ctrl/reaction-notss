"""LastPerson07 Configuration Manager"""
import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_ID: int = int(os.getenv("API_ID"))
    API_HASH: str = os.getenv("API_HASH")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/lastperson07_db")
    OWNER_ID: int = int(os.getenv("OWNER_ID"))
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL"))
    BOT_USERNAME: str = os.getenv("BOT_USERNAME").replace("@", "")

    class Config:
        env_file = ".env"

config = Settings()
