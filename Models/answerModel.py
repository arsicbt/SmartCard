from .baseModel import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re


class Answer(BaseModel):
    """
    Answer Model:
    - Lié à une Question
    - is_correct : indique si c'est la bonne réponse (pour quiz) 
    """
    
    def __init__(
        self,
        answer_text: str,
        question_id: str,
        is_correct: bool=False
    ):
        
        super().__init__()
        
        # ********************************************************
        # DATA VALIDATION
        # ********************************************************
            
        if not answer_text or len(answer_text.strip()) == 0:
            raise ValueError("Le text de la reponse ne peut pas etre vide")
        
        if len(question_text) > 50:
            raise ValueError("La reponse est trop longue")
        
        self.answer_text = answer_text.strip()
        self.question_id = question_id
        self.is_correct = is_correct=False
        
    # ********************************************************
    # SERIALIZATION
    # ********************************************************
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        return data
    
    
    def __repr__(self) -> str:
        correct_marker = "✓" if self.is_correct else "✗"
        return f"<Answer(id={self.id[:8]}, correct={correct_marker})"
