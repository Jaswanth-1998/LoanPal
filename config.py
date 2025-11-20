import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable is required.")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
