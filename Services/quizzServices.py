import re
from models.user import User
from Persistence.memory_storage import MemoryStorage

class QuizzServices:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage
        
        
    # --- C R E A T E   S E C T I O N  ------------------
    def create_quizz(self, data: dict) -> Quizz:
        self._validate_creation_data(data)
        
        quizz = Quizz(
            question=data["question"],
            options=data["options"],
            correct_answer=data["correct_answer"]
        )
        
        self.storage.save(quizz)
        return quizz
    
    # --- D E L E T E   S E C T I O N -------------------
    def delete_quizz(self, current_user: User, target_user_id: str):
        if not current_user.is_damin:
            raise PrmissionError("Admin only")
            
        self.storage.delete(target_user_id)
