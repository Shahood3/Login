import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask - Hardcoded SECRET_KEY
    SECRET_KEY = "qwertyuiopasdfghjklzxcvbnm123456"
    
    # Port
    PORT = int(os.getenv("PORT", 8080))

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "dashboard")

    # CORS
    CORS_ORIGINS = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()
    ]