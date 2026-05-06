"""
Конфигурация приложения TestLearn
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./testlearn.db")
DB_NAME = os.getenv("TESTLEARN_DB", "testlearn.db")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Admin credentials (should be changed in production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")  # Should be set in production

# Application settings
APP_NAME = "TestLearn"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
