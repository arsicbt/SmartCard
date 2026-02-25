import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

class TokenManager:
    """Gestion des tokens JWT"""

    # SÉCURITÉ : Cette clé doit être en variable d'environnement
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-CHANGE-ME')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 heure

    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.refresh_secret = secret_key + "_refresh"

    @classmethod
    def create_access_token(cls, user_id: str, email: str) -> str:
        """
        Crée un token (30min) et un refresh (7h) JWT pour l'utilisateur
        """
        # Access token (court)
        access_token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'exp': now + timedelta(minutes=30),
            'iat': now
        }, self.secret_key, algorithm='HS256')
        
        # Refresh token (long)
        refresh_token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'exp': now + timedelta(days=7),
            'iat': now
        }, self.refresh_secret, algorithm='HS256')
        
        return access_token, refresh_token
    
    @classmethod
    def decode_access_token(self, token):
        """Décode l'access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload.get('type') != 'access':
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def decode_refresh_token(self, token):
        """Décode le refresh token"""
        try:
            payload = jwt.decode(token, self.refresh_secret, algorithms=['HS256'])
            if payload.get('type') != 'refresh':
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None