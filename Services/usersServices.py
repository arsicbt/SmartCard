"""
Users Service - Logique métier pour les utilisateurs

Utilise :
- Utils/inputSecurity.py pour validation
- Utils/passwordSecurity.py pour hash
- Models/userModel.py pour les données
"""

from Models.userModel import User
from Utils.inputSecurity import InputValidator
from Utils.passwordSecurity import PasswordManager
from typing import Optional, Dict, Tuple


class UserService:
    """
    Service de gestion des utilisateurs
    
    Logique métier PURE (pas de dépendances HTTP)
    """
    
    def __init__(self, storage):
        """
        Args:
            storage: Instance de DBStorage
        """
        self.storage = storage
    
    # ********************************************************
    # CREATE
    # ********************************************************
    
    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        name: Optional[str] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Crée un nouvel utilisateur
        
        Utilise :
        - InputValidator pour validation email/password
        - PasswordManager pour hash
        
        Args:
            first_name: Prénom
            last_name: Nom
            email: Email
            password: Mot de passe en clair
            name: Pseudo optionnel
        
        Returns:
            Tuple (User créé, message d'erreur)
        """
        # Validation avec Utils
        user, error = User.validate_and_create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            name=name
        )
        
        if error:
            return None, error
        
        # Vérifier unicité email
        existing_users = self.storage.filter_by('User', email=email)
        if existing_users:
            return None, "Un utilisateur avec cet email existe déjà"
        
        # Sauvegarder
        self.storage.new(user)
        self.storage.save()
        
        return user, None
    
    # ********************************************************
    # READ
    # ********************************************************
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            User ou None
        """
        user = self.storage.get('User', user_id)
        if user and not user.is_deleted():
            return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        
        Args:
            email: Email de l'utilisateur
        
        Returns:
            User ou None
        """
        users = self.storage.filter_by('User', email=email.lower().strip())
        if users and not users[0].is_deleted():
            return users[0]
        return None
    
    def get_all_users(self, include_deleted: bool = False) -> list[User]:
        """
        Récupère tous les utilisateurs
        
        Args:
            include_deleted: Inclure les utilisateurs supprimés
        
        Returns:
            Liste d'utilisateurs
        """
        users_dict = self.storage.all('User')
        users = list(users_dict.values())
        
        if not include_deleted:
            users = [u for u in users if not u.is_deleted()]
        
        return users
    
    # ********************************************************
    # UPDATE
    # ********************************************************
    
    def update_user(
        self,
        user_id: str,
        data: Dict[str, any]
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Met à jour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            data: Données à mettre à jour
        
        Returns:
            Tuple (User mis à jour, message d'erreur)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None, "Utilisateur non trouvé"
        
        # Champs modifiables
        updatable_fields = ['first_name', 'last_name', 'name', 'is_verified']
        
        # Champs protégés
        protected_fields = ['id', 'email', 'password', 'created_at', 'updated_at', 'deleted_at']
        
        updated = False
        for key, value in data.items():
            if key in protected_fields:
                continue
            
            if key in updatable_fields and hasattr(user, key):
                # Sanitize les strings
                if isinstance(value, str):
                    value = InputValidator.sanitize_string(value)
                
                setattr(user, key, value)
                updated = True
        
        if updated:
            user.update_timestamp()
            self.storage.save()
        
        return user, None
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
        
        Returns:
            Tuple (success, message d'erreur)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "Utilisateur non trouvé"
        
        # Vérifier l'ancien mot de passe
        if not user.verify_password(old_password):
            return False, "Ancien mot de passe incorrect"
        
        # Valider le nouveau mot de passe
        is_valid, error = InputValidator.validate_password(new_password)
        if not is_valid:
            return False, error
        
        # Hash et sauvegarder
        user.password = PasswordManager.hash_password(new_password)
        user.update_timestamp()
        self.storage.save()
        
        return True, None
    
    # ********************************************************
    # DELETE
    # ********************************************************
    
    def delete_user(
        self,
        user_id: str,
        hard_delete: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Supprime un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            hard_delete: Suppression définitive ou soft delete
        
        Returns:
            Tuple (success, message d'erreur)
        """
        user = self.storage.get('User', user_id)
        if not user:
            return False, "Utilisateur non trouvé"
        
        self.storage.delete(user, hard_delete=hard_delete)
        self.storage.save()
        
        return True, None
    
    # ********************************************************
    # AUTHENTICATION
    # ********************************************************
    
    def authenticate(
        self,
        email: str,
        password: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authentifie un utilisateur
        
        Args:
            email: Email
            password: Mot de passe en clair
        
        Returns:
            Tuple (User authentifié, message d'erreur)
        """
        user = self.get_user_by_email(email)
        if not user:
            return None, "Email ou mot de passe incorrect"
        
        if not user.verify_password(password):
            return None, "Email ou mot de passe incorrect"
        
        # Mettre à jour last_login
        user.update_last_login()
        self.storage.save()
        
        return user, None