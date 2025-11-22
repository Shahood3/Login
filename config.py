import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    PORT = int(os.getenv("PORT", 8080))

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "login")

    # Secret key (use admin setup key for JWT)
    SECRET_KEY = os.getenv("ADMIN_SETUP_KEY", "default_secret_key")

    # CORS
    CORS_ORIGINS = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
    ]
