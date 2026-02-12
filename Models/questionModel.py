"""
Question Model - Modèle question

Hérite de BaseModel et ajoute :
- Colonnes spécifiques (question_text, type, difficulty)
- Logique métier (is_quiz, is_flashcard)
- Relations SQLAlchemy
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from Models.baseModel import BaseModel
from Models.tablesSchema import QuestionType, Difficulty


class Question(BaseModel):
    """
    Modèle Question
    
    Une question peut être un quiz (QCM) ou une flashcard (recto/verso).
    
    Colonnes :
        - theme_id : ID du thème (FK)
        - type : QUIZ ou FLASHCARD (Enum)
        - question_text : Texte de la question
        - difficulty : EASY, MEDIUM ou HARD (Enum)
        - explanation : Explication de la réponse
        - source : Origine (ai_generated ou user_created)
        - times_used : Nombre d'utilisations
        - times_correct : Nombre de fois répondu correctement
    
    Relations :
        - theme : Thème parent
        - answers : Liste des réponses possibles
    """
    
    __tablename__ = 'questions'
    
    # ********************************************************
    # COLONNES SPÉCIFIQUES
    # ********************************************************
    
    theme_id = Column(String(60), ForeignKey('themes.id', ondelete='CASCADE'), nullable=False)
    type = Column(SQLEnum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(Difficulty), default=Difficulty.MEDIUM, nullable=False)
    explanation = Column(Text, nullable=True)
    #source = Column(String(50), default='ai_generated')  # 'ai_generated' ou 'user_created'
    
    # Statistiques
    times_used = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    
    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************
    
    theme = relationship('Theme', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    # ********************************************************
    # INDEX
    # ********************************************************
    
    __table_args__ = (
        Index('idx_questions_theme', 'theme_id'),
        Index('idx_questions_type', 'type'),
        Index('idx_questions_difficulty', 'difficulty'),
    )
    
    # ********************************************************
    # LOGIQUE MÉTIER - TYPE CHECKING
    # ********************************************************
    
    def is_quiz(self) -> bool:
        """
        Vérifie si c'est une question de quiz
        
        Returns:
            True si type == QUIZ
        """
        return self.type == QuestionType.QUIZ
    
    def is_flashcard(self) -> bool:
        """
        Vérifie si c'est une flashcard
        
        Returns:
            True si type == FLASHCARD
        """
        return self.type == QuestionType.FLASHCARD
    
    def get_success_rate(self) -> float:
        """
        Calcule le taux de réussite de cette question
        
        Returns:
            Taux de réussite en pourcentage (0-100)
        """
        if self.times_used == 0:
            return 0.0
        return (self.times_correct / self.times_used) * 100
    
    def increment_usage(self, is_correct: bool = False) -> None:
        """
        Incrémente les statistiques d'utilisation
        
        Args:
            is_correct: La réponse était-elle correcte ?
        """
        self.times_used += 1
        if is_correct:
            self.times_correct += 1
        self.update_timestamp()
    
    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************
    
    def __repr__(self) -> str:
        text_preview = self.question_text[:50] + '...' if len(self.question_text) > 50 else self.question_text
        return f"<Question(id={self.id[:8] if self.id else 'None'}, type={self.type.value if self.type else 'None'}, text='{text_preview}')>"
