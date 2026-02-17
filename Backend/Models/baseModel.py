"""
BaseModel - Classe de base pour tous les modèles SQLAlchemy

Fournit :
- Colonnes communes (id, created_at, updated_at, deleted_at)
- Méthodes utilitaires (to_dict, soft_delete, update_timestamp)
- Héritage SQLAlchemy via Base
"""

from sqlalchemy import Column, String, DateTime
from Models.tablesSchema import Base
from datetime import datetime
from typing import Dict, Any
import uuid


class BaseModel(Base):
    """
    Classe de base pour tous les modèles
    
    Hérite de Base SQLAlchemy et fournit les colonnes/méthodes communes.
    Tous les autres modèles (User, Theme, etc.) héritent de BaseModel.
    
    Colonnes automatiques :
        - id : UUID unique (primary key)
        - created_at : Date de création
        - updated_at : Date de dernière modification  
        - deleted_at : Date de suppression (soft delete)
    
    Méthodes :
        - to_dict() : Sérialise en dictionnaire
        - soft_delete() : Suppression logique
        - is_deleted() : Vérifie si supprimé
        - update_timestamp() : Met à jour updated_at
    """
    
    __abstract__ = True  # Indique que BaseModel n'a pas de table propre
    
    # ********************************************************
    # COLONNES COMMUNES
    # ********************************************************
    
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # ********************************************************
    # MÉTHODES UTILITAIRES
    # ********************************************************
    
    def to_dict(self, include_private: bool = False) -> Dict[str, Any]:
        """
        Sérialise le modèle en dictionnaire
        
        Args:
            include_private: Inclure les champs privés (ex: password)
        
        Returns:
            Dictionnaire contenant tous les attributs
        """
        data = {}
        
        # Parcourir toutes les colonnes de la table
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Formater les dates en ISO
            if isinstance(value, datetime):
                data[column.name] = value.isoformat()
            # Gérer les enums
            elif hasattr(value, 'value'):
                data[column.name] = value.value
            # Garder les autres types tels quels
            else:
                data[column.name] = value
        
        # Supprimer les champs privés par défaut
        if not include_private:
            data.pop('password', None)
            data.pop('password_hash', None)
        
        return data
    
    def soft_delete(self) -> None:
        """
        Suppression logique (soft delete)
        
        Marque l'objet comme supprimé sans le retirer de la BDD.
        Permet de conserver l'historique et les relations.
        """
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_deleted(self) -> bool:
        """
        Vérifie si l'objet est supprimé
        
        Returns:
            True si l'objet a été soft-deleted
        """
        return self.deleted_at is not None
    
    def update_timestamp(self) -> None:
        """Met à jour le timestamp de modification"""
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """Représentation en chaîne de caractères"""
        return f"<{self.__class__.__name__}(id={self.id[:8] if self.id else 'None'})>"
