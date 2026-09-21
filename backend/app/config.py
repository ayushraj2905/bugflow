import os

SECRET_KEY = os.getenv('SECRET_KEY', 'bugflow-super-secret-key-2026-secure-jwt')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bugflow.db')
PROJECT_NAME = 'BugFlow - Software Issue Tracking & Resolution Platform'
VERSION = '2.0.0'
