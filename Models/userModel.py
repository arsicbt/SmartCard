from .baseModel import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re

class User(BaseModel):
    
    # Regex pour validation email (RFC 5322 simplifié)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,  # Déjà hashé avec bcrypt
        name: str,
        is_verified: bool
        ):

        super().__init__()
        
        # Validation email
        if not self.validate_email(email):
            raise ValueError(f"Email invalide: {email}")
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.lower().strip()
        self.password_hash = password_hash
        self.name = name.strip() if name else None
        self.is_verified = is_verified


    
    # ********************************************************************
    # DATA VALIDATION
    # ********************************************************************
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valide le format de l'email"""
        if not email or len(email) > 255:
            return False
        return bool(User.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """
        Valide la sécurité du mdp
        """
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"
        
        if len(password) > 128:
            return False, "Le mot de passe ne peut pas dépasser 128 caractères"
        
        # Vérifier la complexité
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre"
        
        return True, None



    # ********************************************************************
    # SERIALIZATION
    # ********************************************************************
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        Sérialise l'utilisateur, SANS le mdp par défaut
        """
        data = super().to_dict()
        
        if not include_password:
            data.pop('password_hash', None)
        
        return data
    
    def __repr__(self) -> str:
        return f"<User(id={self.id[:8]}, email={self.email})>"
