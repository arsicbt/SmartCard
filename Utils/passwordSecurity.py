import bcrypt
from typing import Optional

class PasswordManager:
    """Gestion sécurisée des mots de passe"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash un mot de passe avec bcrypt
        
        Pourquoi bcrypt ?
        - Lent par design (résiste au brute-force)
        - Ajoute automatiquement un "salt" (rend chaque hash unique)
        - Standard industrie
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Hash sécurisé (stockable en DB)
        """
        # Génère un salt et hash le mot de passe
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = bon équilibre sécurité/performance
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Vérifie si un mot de passe correspond au hash
        
        Args:
            password: Mot de passe fourni par l'utilisateur
            hashed: Hash stocké en DB
            
        Returns:
            True si le mot de passe est correct
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
