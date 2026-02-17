import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables depuis .env

class Config:
    """Configuration centralisée de l'application"""
    
    # SÉCURITÉ : JAMAIS de valeurs en dur en production
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-CHANGE-IN-PROD')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-CHANGE-IN-PROD')
    
    # Database
    DB_TYPE = os.getenv('DB_TYPE', 'file')  # 'file' ou 'db'
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smartcard.db')
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', '12'))
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    
    # CORS (sécurité navigateur)
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate limiting (protection DDoS)
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per hour')

class DevelopmentConfig(Config):
    """Config pour développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Config pour production"""
    DEBUG = False
    TESTING = False
    
    # En prod, les secrets DOIVENT être définis
    @classmethod
    def validate(cls):
        required = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']
        for key in required:
            if getattr(cls, key).startswith('dev-') or 'CHANGE' in getattr(cls, key):
                raise ValueError(f"{key} doit être défini en production!")
