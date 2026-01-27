from .baseModel import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re



class Question(BaseModel):
    """
    Model Question = Quiz + FlashCard
    - type: 'quiz' ou 'flashcard'
    - Relation avec Theme et Answers
    """

    VALID_TYPES = {'quiz', 'flashcard'}
    VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}

    def __init__(
        self,
        question_text: str,
        theme_id: str,
        question_type: str = 'quiz',
        difficulty: str = 'medium'
    );
        super()__init__()
        
        # ********************************************************
        # DATA VALIDATION
        # ********************************************************
        
        if not question_text or len(question_text.strip()) == 0:
            raise ValueError("Le texte de la question ne peut pas etre vide")
        
        if len(question_text) > 50:
            raise ValueError("La question est trop longue")
        
        if question_type not in self.VALID_TYPES:
            raise ValueError(f"LE type doit etre : {self.VALID_TYPES}")
        
        id diffcilculty not in self.VALID_DIFFICULTIES:
            raise VelueError(f"La difficulté doit etre: {self.VALID_DIFFICULTIES}")
        
        self.question_text = question_text
        self.theme_id = theme_id
        self.type = question_type
        self.difficulty = difficulty
        
        # Liste des IDs des reponses
        self.answer_ids: List[str] = []
    
    
    des add_answer_id(self, answer_id: str) -> None:
        if answer_id not in self.answer_ids:
            self.answer_ids.append(answer_id)
            self.update_timestamp()
            
    def is_quiz(self) -> bool:
        """
        Verifie si c'est une question de quizz
        """
        return self.type == 'quiz'
    
    def is_flashcard(self) -> bool:
        """
        Verifie si c'est une question de flashcard
        """
        return self.type == 'flashcard'


    # ********************************************************
    # SERIALIZATION
    # ********************************************************
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        return data

    def __repr__(self) -> str:
        return f"<Question(id={self.id[:8]}, type={self.type}, difficulty={self.difficulty})"
