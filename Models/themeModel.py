from .baseModel import BaseModel
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re
import json


class Theme(BaseModel):
    def __init__(
        self, 
        name: str,
        keywords: List[str],
        user_id: str,
        description: Optional[str] = None
    ):
    
        super().__init__()
    
    
        # ********************************************************************
        # DATA VALIDATION
        # ********************************************************************
        
        if not name or len(name.strip()) == 0:
            raise ValueError("Le theme a besoin d'un nom")
        
        if keywords or len(keywords) == 0:
            raise ValueError("Le theme a besoin d'au moins 1 mot clé")
        
        self.name = name.strip()
        self.keywords = [k.lower().strip() for k in keywords id k.strip()]
        self.user_id = user_id
        self.description = description.strip() if description else None
        
     
     
    # ********************************************************
    # DATA ANALYSE
    # ********************************************************
       
    def matches_keywords(self, search_keywords: List[str], threshold: float = 0.5) -> bool:
        """
        Verifie si les mot-clès de recherche correspondent au theme
        threshold: pourcentage de correspondance (0.5 = 50%)
        """
        if not search_keywords:
            return False
        
        search_set = set(k.lower().strip() for k in search_keywords)
        theme_set = set(self.keywords)
        
        # Intersection des mot clés 
        matches = search_set & theme_set
        
        # Calcul du ratio de correspondance 
        match_radio = len(matches) / len(search_set)
         
        return match_ratio >= threshold
     
     
    # ********************************************************
    # SERIALIZATION
    # ********************************************************
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        return data
    
    def __rep__(self) -> str:
        return f"<Theme(id={self.id[:8]}, name={self.name})>"
        