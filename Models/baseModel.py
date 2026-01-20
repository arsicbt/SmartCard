import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re
import json


class BaseModel:
    
    # ********************************************************
    # ATTRIBUTS
    # ********************************************************
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    
    
    # ********************************************************
    # SERIALIZATION
    # ********************************************************
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise le modèle en dictionnaire"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                data[key] = value
            else:
                data[key] = value
        return data
    
    def soft_delete(self) -> None:
        """Suppression logique (soft delete)"""
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def is_deleted(self) -> bool:
        """Vérifie si l'objet est supprimé"""
        return self.deleted_at is not None
    
    def update_timestamp(self) -> None:
        """Met à jour le timestamp de modification"""
        self.updated_at = datetime.now(timezone.utc)
