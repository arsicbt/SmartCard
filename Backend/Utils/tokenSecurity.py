import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

class TokenManager:
    """Gestion des tokens JWT"""

    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.refresh_secret = secret_key + "_refresh"
        self.algorithm = 'HS256'

    def generate_tokens(self, user_id: str, email: str):
        """
        Crée un access token (1h) et un refresh token (7j)
        """
        now = datetime.utcnow()
        
        # Access token (court)
        access_token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'exp': now + timedelta(minutes=30),
            'iat': now
        }, self.secret_key, algorithm=self.algorithm)
        
        # Refresh token (long)
        refresh_token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'exp': now + timedelta(days=7),
            'iat': now
        }, self.refresh_secret, algorithm=self.algorithm)
        
        return access_token, refresh_token
    
    def decode_access_token(self, token):
        """Décode l'access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get('type') != 'access':
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def decode_refresh_token(self, token):
        """Décode le refresh token"""
        try:
            payload = jwt.decode(token, self.refresh_secret, algorithms=[self.algorithm])
            if payload.get('type') != 'refresh':
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'ed52532ea8a237c39bcfa758417560d6eed993c0df3e01033a71fa458e769eb0')
token_manager = TokenManager(SECRET_KEY)