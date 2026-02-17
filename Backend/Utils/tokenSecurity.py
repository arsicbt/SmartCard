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

    @classmethod
    def create_access_token(cls, user_id: str, email: str) -> str:
        """
        Crée un token JWT pour l'utilisateur
        
        Le token contient :
        - user_id : pour identifier l'utilisateur
        - email : info supplémentaire
        - exp : date d'expiration (sécurité)
        - iat : date de création (traçabilité)
        
        Args:
            user_id: ID unique de l'utilisateur
            email: Email de l'utilisateur
            
        Returns:
            Token JWT encodé
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token
    
    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict]:
        """
        Décode et valide un token JWT
        
        Vérifie :
        - Signature valide
        - Token non expiré
        - Format correct
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token expiré
            return None
        except jwt.InvalidTokenError:
            # Token invalide (signature incorrecte, format incorrect...)
            return None
