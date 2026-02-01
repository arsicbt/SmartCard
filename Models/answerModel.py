"""
Answer Model - Modèle réponse

Hérite de BaseModel et ajoute :
- Colonnes spécifiques (answer_text, is_correct, order_position)
- Relations SQLAlchemy
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from Models.baseModel import BaseModel


class Answer(BaseModel):
    """
    Modèle Réponse
    
    Une réponse est liée à une question.
    - Pour un QUIZ : 4 réponses (1 correcte, 3 fausses)
    - Pour une FLASHCARD : 1 réponse (la réponse du verso)
    
    Colonnes :
        - question_id : ID de la question (FK)
        - answer_text : Texte de la réponse
        - is_correct : Réponse correcte ou non
        - order_position : Ordre d'affichage (pour les quiz)
    
    Relations :
        - question : Question parente
    """
    
    __tablename__ = 'answers'
    
    # ********************************************************
    # COLONNES SPÉCIFIQUES
    # ********************************************************
    
    question_id = Column(String(60), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order_position = Column(Integer, default=0)
    
    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************
    
    question = relationship('Question', back_populates='answers')
    
    # ********************************************************
    # INDEX
    # ********************************************************
    
    __table_args__ = (
        Index('idx_answers_question', 'question_id'),
        Index('idx_answers_correct', 'is_correct'),
    )
    
    # ********************************************************
    # LOGIQUE MÉTIER
    # ********************************************************
    
    def mark_as_correct(self) -> None:
        """Marque cette réponse comme correcte"""
        self.is_correct = True
        self.update_timestamp()
    
    def mark_as_incorrect(self) -> None:
        """Marque cette réponse comme incorrecte"""
        self.is_correct = False
        self.update_timestamp()
    
    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************
    
    def __repr__(self) -> str:
        correct_symbol = "✓" if self.is_correct else "✗"
        text_preview = self.answer_text[:30] + '...' if len(self.answer_text) > 30 else self.answer_text
        return f"<Answer(id={self.id[:8] if self.id else 'None'}, text='{text_preview}', correct={correct_symbol})>"
