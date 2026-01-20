from .coreModel import CoreModel


class CardModel(CoreModel):
    
    # --- A T T R I B U T S ---------------------------------
    def __init__(self, question, answer):
        super().__init__()
        self.question = question
        self.answer = answer

    # --- S E R I A L I Z A T I O N -------------------------
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "question": self.question,
            "answer": self.answer
        })
        return data
