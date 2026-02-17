from Models.userModel import User
from Utils.passwordSecurity import PasswordManager
from Utils.tokenSecurity import TokenManager
from Utils.inputSecurity import InputValidator
from typing import Optional, Dict, Tuple


class AuthService:
    """Service gérant l'authentification"""
    
    def __init__(self, storage):
        """
        Args:
            storage: Instance de FileStorage ou DBStorage
        """
        self.storage = storage
    
    def register(self, email: str, password: str, name: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Enregistre un nouvel utilisateur
        
        
        Processus sécurisé :
        1. Validation des entrées
        2. Vérification unicité email
        3. Hash du mot de passe
        4. Création user
        5. Génération token
        
        Returns:
            (success, user_data, error_message)
        """
        # 1. VALIDATION
        is_valid, error = InputValidator.validate_email(email)
        if not is_valid:
            return False, None, error
        
        is_valid, error = InputValidator.validate_password(password)
        if not is_valid:
            return False, None, error
        
        name = InputValidator.sanitize_string(name, max_length=100)
        if not name:
            return False, None, "Nom requis"
        
        # 2. VÉRIFICATION UNICITÉ
        existing_user = self.storage.get_by_email(User, email)
        if existing_user:
            return False, None, "Email déjà utilisé"
        
        # 3. HASH DU MOT DE PASSE
        hashed_password = PasswordManager.hash_password(password)
        
        # 4. CRÉATION USER
        user = User(
            email=email,
            password=hashed_password,
            name=name
        )
        self.storage.new(user)
        self.storage.save()
        
        # 5. GÉNÉRATION TOKEN
        token = TokenManager.create_access_token(user.id, user.email)
        
        return True, {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'token': token
        }, None
    
    def login(self, email: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Connecte un utilisateur
        
        Processus :
        1. Validation email
        2. Recherche user
        3. Vérification mot de passe
        4. Génération token
        """
        # 1. VALIDATION
        is_valid, error = InputValidator.validate_email(email)
        if not is_valid:
            return False, None, "Identifiants invalides"  # Message générique (sécurité)
        
        # 2. RECHERCHE USER
        user = self.storage.get_by_email(User, email)
        if not user:
            return False, None, "Identifiants invalides"
        
        # 3. VÉRIFICATION MOT DE PASSE
        if not PasswordManager.verify_password(password, user.password):
            return False, None, "Identifiants invalides"
        
        # 4. GÉNÉRATION TOKEN
        token = TokenManager.create_access_token(user.id, user.email)
        
        return True, {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'token': token
        }, None
