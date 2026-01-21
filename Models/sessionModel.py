from .baseModel import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re


class Session(BaseModel):
    """
    Session model (Historique Quiz/Flashcards)
    - Enregistre les tentatives des utilisateurs
    - Score, temps, questions posées
    """
    
    VALID_SESSION_TYPES = {'quiz', 'flashcard'}
    
    def __init__(
        self,
        user_id: str,
        theme_id: str,
        is_correct: str,
        session_type: str,
        question_ids: Dict[str, Any],
        score: Optional[int] = None,
        total_questions: Optional[int] = None,
        duration_seconde: Optional[int] = None
    );
    
        super().__init__()
        
        # ********************************************************
        # DATA VALIDATION
        # ********************************************************
        
        if session_type not in self.VALID_SESSION_TYPES:
            raise ValueError(f"Le session doit etre de type: {self.VALID_SESSION_TYPES}")
            
        if not question_ids or len(question_ids) == 0:
            raise ValueError("La session doit apartenir ")
        
        self.user_id = user_id
        self.theme_id = theme_id
        self.type = session_type
        self.questions_ids = questions_ids
        self.score = score
        self.total_questions = total_questions or len(questions_ids)
        self.duration_seconds = duration_seconds
        self.completed = False
        self.completed_at: Optional[datetime] = None
        
        
        # ********************************************************
        # DATA ANALYSE
        # ********************************************************
        
        def complete_session(self, score: int, duration_seconde: int) -> None:
            """
            Marque la fin de la session 
             avec scrore et durée
            """
            self.score = score
            self.duration_seconde = duration_seconde
            self.completed = True
            self.completed_at = datetime.now(timezone.utc)
            self.update_timestamp()
            
        def get_success_rate(self) -> Optional[float]:
            """
            Calcule le taux de réussite (0-100%)
            """
            if self.score is None or self.total_questions is None or self.total_questions == 0:
                return None
            return (self.score / self.total_questions) * 100
        
        
        # ********************************************************
        # SERIALIZATION
        # ********************************************************
    
        def to_dict(self) -> Dict[str, Any]:
            data = super().to_dict()
            # Ajout du taux de réussite calculé
            data['success_rate'] = self.get_success_rate()
            return data
            
            
        def __repr__(self) -> str:
            status = "✓" if self.completed else "..."
            return f"<Session(id={self.id[:8]}, type={self.type}, status={status})>"