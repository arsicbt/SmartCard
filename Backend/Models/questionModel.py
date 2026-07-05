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
from typing import Dict, Any


class Question(BaseModel):
    """Modèle Question.

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
    # source = Column(String(50), default='ai_generated')  # 'ai_generated' ou 'user_created'

    # Statistiques
    times_used = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)

    # ********************************************************
    # RELATIONS SQLALCHEMY
    # ********************************************************

    theme = relationship('Theme', back_populates='questions')
    answers = relationship(
        'Answer',
        back_populates='question',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

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
        """Vérifie si c'est une question de quiz.

        Returns:
            True si type == QUIZ
        """
        return self.type == QuestionType.QUIZ

    def is_flashcard(self) -> bool:
        """Vérifie si c'est une flashcard.

        Returns:
            True si type == FLASHCARD
        """
        return self.type == QuestionType.FLASHCARD

    def get_success_rate(self) -> float:
        """Calcule le taux de réussite de cette question.

        Returns:
            Taux de réussite en pourcentage (0-100)
        """
        if self.times_used == 0:
            return 0.0
        return (self.times_correct / self.times_used) * 100

    def increment_usage(self, is_correct: bool = False) -> None:
        """Incrémente les statistiques d'utilisation.

        Args:
            is_correct: La réponse était-elle correcte ?
        """
        self.times_used += 1
        if is_correct:
            self.times_correct += 1
        self.update_timestamp()

    # ********************************************************
    # SÉRIALISATION
    # ********************************************************

    def to_dict(self, include_private: bool = False,
                include_relations: bool = True) -> Dict[str, Any]:
        """Sérialise la question en dictionnaire.

        Surcharge BaseModel.to_dict pour exposer la relation `answers`
        directement dans le JSON renvoyé, au lieu d'un appel séparé.

        Args:
            include_private: Inclure les champs privés
            include_relations: Inclure la liste des réponses (clé 'answers')

        Returns:
            Dictionnaire de la question. Si include_relations est True,
            contient la clé 'answers' avec les réponses ACTIVES
            (deleted_at IS NULL) triées par order_position.

        Note:
            Les réponses soft-deleted sont exclues pour rester cohérent
            avec le comportement de DBStorage (filter_by/get/all), car la
            relation SQLAlchemy charge sinon toutes les lignes.
        """
        data = super().to_dict(include_private=include_private)

        if include_relations:
            active_answers = [a for a in self.answers if a.deleted_at is None]
            active_answers.sort(
                key=lambda a: a.order_position if a.order_position is not None else 0
            )
            data['answers'] = [
                a.to_dict(include_private=include_private) for a in active_answers
            ]

        return data

    # ********************************************************
    # REPRÉSENTATION
    # ********************************************************

    def __repr__(self) -> str:
        """Retourne une représentation lisible de la question."""
        text_preview = self.question_text[:50] + '...' if len(self.question_text) > 50 else self.question_text
        return f"<Question(id={self.id[:8] if self.id else 'None'}, type={self.type.value if self.type else 'None'}, text='{text_preview}')>"
