"""
User Model - Modèle utilisateur

Hérite de BaseModel et ajoute :
- Colonnes spécifiques (email, password, name, etc.)
- Logique métier (validation via Utils)
- Relations SQLAlchemy
"""

from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship
from Models.baseModel import BaseModel
from Utils.inputSecurity import InputValidator
from Utils.passwordSecurity import PasswordManager
from typing import Optional, Tuple


class User(BaseModel):
    """
    Modèle Utilisateur
    
    Colonnes :
        - first_name : Prénom
        - last_name : Nom de famille
        - email : Email unique (authentification)
        - password : Hash bcrypt du mot de passe
        - name : Pseudo/nom d'affichage
        - is_verified : Email vérifié
        - is_admin : Privilèges administrateur
        - verification_token : Token de vérification email
        - last_login_at : Dernière connexion
    
    Relations :
        - themes : Liste des thèmes créés
        - sessions : Liste des sessions d'étude
    """
    
    __tablename__ = 'users'
    
    # ********************************************************
    # COLONNES SPÉCIFIQUES
    # ********************************************************
    
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    name = Column(String(100), nullable=True)
    
    # Vérification email
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    last_login_at = Column(String, nullable=True)
    
    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************
    
    themes = relationship('Theme', back_populates='user', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    
    # ********************************************************
    # INDEX
    # ********************************************************
    
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_deleted', 'deleted_at'),
        Index('idx_users_admin', 'is_admin'),
    )
    
    # ********************************************************
    # VALIDATION AVEC UTILS
    # ********************************************************
    
    @staticmethod
    def validate_and_create(
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        name: Optional[str] = None,
        is_admin: bool = False
    ) -> Tuple[Optional['User'], Optional[str]]:
        """
        Valide les données et crée un utilisateur
        
        Utilise Utils pour :
        - Valider email (InputValidator)
        - Valider password (InputValidator)
        - Hasher password (PasswordManager)
        
        Args:
            first_name: Prénom
            last_name: Nom
            email: Email
            password: Mot de passe en clair
            is_admin: Privilege administrateur
            name: Pseudo optionnel
        
        Returns:
            Tuple (User créé, message d'erreur)
        """
        # Validation email avec Utils
        is_valid_email, email_error = InputValidator.validate_email(email)
        if not is_valid_email:
            return None, email_error
        
        # Validation password avec Utils
        is_valid_pwd, pwd_error = InputValidator.validate_password(password)
        if not is_valid_pwd:
            return None, pwd_error
        
        # Sanitize inputs avec Utils
        first_name = InputValidator.sanitize_string(first_name)
        last_name = InputValidator.sanitize_string(last_name)
        if name:
            name = InputValidator.sanitize_string(name)
        
        # Hash password avec Utils
        password_hash = PasswordManager.hash_password(password)
        
        # Créer l'utilisateur
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email.lower().strip(),
            password=password_hash,
            name=name,
            is_verified=False,
            is_admin=is_admin
        )
        
        return user, None
    
    def verify_password(self, password: str) -> bool:
        """
        Vérifie un mot de passe avec Utils
        
        Args:
            password: Mot de passe en clair à vérifier
        
        Returns:
            True si le mot de passe correspond
        """
        return PasswordManager.verify_password(password, self.password)
    
    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion"""
        from datetime import datetime
        self.last_login_at = datetime.utcnow()
        self.update_timestamp()
    
    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************
    
    def __repr__(self) -> str:
        return f"<User(id={self.id[:8] if self.id else 'None'}, email={self.email})>"