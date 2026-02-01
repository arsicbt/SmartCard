"""
Theme Model - Modèle thème

Hérite de BaseModel et ajoute :
- Colonnes spécifiques (name, keywords, description)
- Logique métier (matches_keywords)
- Relations SQLAlchemy
"""

from sqlalchemy import Column, String, Text, JSON, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from Models.baseModel import BaseModel
from typing import List


class Theme(BaseModel):
    """
    Modèle Thème
    
    Un thème regroupe des questions sur un sujet particulier.
    
    Colonnes :
        - user_id : ID du propriétaire (FK)
        - name : Nom du thème
        - description : Description
        - keywords : Liste de mots-clés (JSON)
        - questions_count : Nombre de questions
        - times_used : Popularité
    
    Relations :
        - user : Utilisateur propriétaire
        - questions : Liste des questions du thème
        - sessions : Sessions utilisant ce thème
    """
    
    __tablename__ = 'themes'
    
    # ********************************************************
    # COLONNES SPÉCIFIQUES
    # ********************************************************
    
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=False, default=list)  # Liste de mots-clés
    
    # Statistiques
    questions_count = Column(Integer, default=0)
    times_used = Column(Integer, default=0)
    
    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************
    
    user = relationship('User', back_populates='themes')
    questions = relationship('Question', back_populates='theme', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='theme')
    
    # ********************************************************
    # CONTRAINTES ET INDEX
    # ********************************************************
    
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_theme_name'),
        Index('idx_themes_user', 'user_id'),
    )
    
    # ********************************************************
    # LOGIQUE MÉTIER - KEYWORDS MATCHING
    # ********************************************************
    
    def matches_keywords(self, search_keywords: List[str], threshold: float = 0.5) -> bool:
        """
        Vérifie si les mots-clés de recherche correspondent au thème
        
        Utilisé pour détecter si un document correspond à un thème existant.
        
        Args:
            search_keywords: Mots-clés à rechercher
            threshold: Pourcentage de correspondance minimum (0.5 = 50%)
        
        Returns:
            True si le seuil de correspondance est atteint
        
        Exemple:
            >>> theme = Theme(keywords=['python', 'flask', 'api'])
            >>> theme.matches_keywords(['python', 'django'], threshold=0.5)
            True  # 1 match sur 2 = 50%
        """
        if not search_keywords or not self.keywords:
            return False
        
        # Normaliser en minuscules
        search_set = set(k.lower().strip() for k in search_keywords if k.strip())
        theme_set = set(k.lower().strip() for k in self.keywords if k.strip())
        
        if not search_set:
            return False
        
        # Calculer l'intersection
        matches = search_set & theme_set
        
        # Calculer le ratio de correspondance
        match_ratio = len(matches) / len(search_set)
        
        return match_ratio >= threshold
    
    def add_keyword(self, keyword: str) -> None:
        """
        Ajoute un mot-clé au thème
        
        Args:
            keyword: Mot-clé à ajouter
        """
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.update_timestamp()
    
    def remove_keyword(self, keyword: str) -> bool:
        """
        Retire un mot-clé du thème
        
        Args:
            keyword: Mot-clé à retirer
        
        Returns:
            True si le mot-clé a été retiré
        """
        keyword = keyword.lower().strip()
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.update_timestamp()
            return True
        return False
    
    def increment_usage(self) -> None:
        """Incrémente le compteur d'utilisation"""
        self.times_used += 1
        self.update_timestamp()
    
    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************
    
    def __repr__(self) -> str:
        return f"<Theme(id={self.id[:8] if self.id else 'None'}, name={self.name}, questions={self.questions_count})>"