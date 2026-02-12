"""
Session Model - Modèle session d'étude

Hérite de BaseModel et ajoute :
- Colonnes spécifiques (type, score, questions_ids)
- Logique métier (complete_session, get_success_rate)
- Relations SQLAlchemy
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from Models.baseModel import BaseModel
from Models.tablesSchema import SessionType
from datetime import datetime
from typing import List


class Session(BaseModel):
    """
    Modèle Session
    
    Une session représente une séance d'étude (quiz ou flashcards).
    
    Colonnes :
        - user_id : ID de l'utilisateur (FK)
        - theme_id : ID du thème (FK)
        - type : QUIZ ou FLASHCARD (Enum)
        - questions_count : Nombre de questions
        - questions_ids : Liste des IDs de questions (JSON)
        - score : Score obtenu
        - max_score : Score maximum
        - started_at : Date/heure de début
        - completed_at : Date/heure de fin
    
    Relations :
        - user : Utilisateur
        - theme : Thème
    """
    
    __tablename__ = 'sessions'
    
    # ********************************************************
    # COLONNES SPÉCIFIQUES
    # ********************************************************
    
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    theme_id = Column(String(60), ForeignKey('themes.id', ondelete='SET NULL'), nullable=True)
    type = Column(SQLEnum(SessionType), nullable=False)
    
    # Configuration
    questions_count = Column(Integer, nullable=False)
    questions_ids = Column(JSON, nullable=False, default=list)
    
    # Résultats
    score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    
    # Timestamps spécifiques
    started_at = Column(Column(String, default=datetime.utcnow, nullable=False))
    completed_at = Column(Column(String, nullable=True))
    
    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************
    
    user = relationship('User', back_populates='sessions')
    theme = relationship('Theme', back_populates='sessions')
    
    # ********************************************************
    # INDEX
    # ********************************************************
    
    __table_args__ = (
        Index('idx_sessions_user', 'user_id'),
        Index('idx_sessions_theme', 'theme_id'),
        Index('idx_sessions_type', 'type'),
        Index('idx_sessions_completed', 'completed_at'),
    )
    
    # ********************************************************
    # LOGIQUE MÉTIER - SESSION MANAGEMENT
    # ********************************************************
    
    def complete_session(self, score: int, max_score: int) -> None:
        """
        Termine la session et enregistre le score
        
        Args:
            score: Score obtenu
            max_score: Score maximum possible
        """
        self.completed_at = datetime.utcnow()
        self.score = score
        self.max_score = max_score
        self.update_timestamp()
    
    def get_success_rate(self) -> float:
        """
        Calcule le taux de réussite de la session
        
        Returns:
            Taux de réussite en pourcentage (0-100)
            Retourne 0 si la session n'est pas terminée ou max_score = 0
        """
        if not self.completed_at or not self.max_score or self.max_score == 0:
            return 0.0
        
        return (self.score / self.max_score) * 100
    
    def is_completed(self) -> bool:
        """
        Vérifie si la session est terminée
        
        Returns:
            True si completed_at est défini
        """
        return self.completed_at is not None
    
    def get_duration_seconds(self) -> int:
        """
        Calcule la durée de la session en secondes
        
        Returns:
            Durée en secondes, ou 0 si pas terminée
        """
        if not self.completed_at:
            return 0
        
        duration = self.completed_at - self.started_at
        return int(duration.total_seconds())
    
    def add_question_id(self, question_id: str) -> None:
        """
        Ajoute un ID de question à la session
        
        Args:
            question_id: ID de la question
        """
        if question_id not in self.questions_ids:
            self.questions_ids.append(question_id)
            self.update_timestamp()
    
    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************
    
    def __repr__(self) -> str:
        status = "completed" if self.is_completed() else "in_progress"
        score_str = f"{self.score}/{self.max_score}" if self.score is not None else "N/A"
        return f"<Session(id={self.id[:8] if self.id else 'None'}, type={self.type.value if self.type else 'None'}, score={score_str}, status={status})>"
