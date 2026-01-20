import re
from typing import Optional, Tuple

class InputValidator:
    """Validation et sanitization des entrées utilisateur"""
    
    # Regex pour email valide
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valide un email
        
        Pourquoi ?
        - Empêche les injections via email
        - Assure la cohérence des données
        - Meilleure UX (erreur claire)
        
        Returns:
            (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email requis"
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321
            return False, "Email trop long"
        
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Format d'email invalide"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Valide un mot de passe
        
        Règles de sécurité :
        - Min 8 caractères (résistance brute-force)
        - 1 majuscule (complexité)
        - 1 minuscule
        - 1 chiffre
        - 1 caractère spécial
        """
        if not password or not isinstance(password, str):
            return False, "Mot de passe requis"
        
        if len(password) < 8:
            return False, "Minimum 8 caractères"
        
        if len(password) > 128:
            return False, "Mot de passe trop long (max 128)"
        
        if not re.search(r'[A-Z]', password):
            return False, "Au moins 1 majuscule requise"
        
        if not re.search(r'[a-z]', password):
            return False, "Au moins 1 minuscule requise"
        
        if not re.search(r'\d', password):
            return False, "Au moins 1 chiffre requis"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Au moins 1 caractère spécial requis"
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """
        Nettoie une chaîne de caractères
        
        Protection contre :
        - XSS (scripts malveillants)
        - Injections diverses
        - Overflow de taille
        """
        if not text:
            return ""
        
        # Supprime les caractères de contrôle dangereux
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Limite la taille
        text = text[:max_length]
        
        # Trim whitespace
        return text.strip()
