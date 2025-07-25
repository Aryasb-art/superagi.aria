import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://superagi_user:KlbTE6LOdFQJOhs9SJ0yUAOZxpdRZ82F@dpg-d1jd9mqli9vc739oe120-a.oregon-postgres.render.com:5432/superagi_rb2d")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5000", "http://localhost:8080", "http://localhost:8000", "*"]

settings = Settings()
