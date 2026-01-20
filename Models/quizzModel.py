from .coreModel import CoreModel


class Quiz(CoreModel):


    # --- A T T R I B U T S ---------------------------------
    __allowed_fields__ = ["question", "options", "correct_answer"]

    def __init__(self, question, options, correct_answer):
        super().__init__()
        self.question = question
        self.options = options  # dict ou list
        self.correct_answer = correct_answer

        self.validate()


    # --- H E L P E R S --------------------------------------
    def validate(self):
        if not self.question:
            raise ValueError("Question is required")

        if not self.options or len(self.options) < 2:
            raise ValueError("At least two options are required")

        if self.correct_answer not in self.options:
            raise ValueError("Correct answer must be in options")

    def is_correct(self, answer):
        """Check a single answer"""
        return answer == self.correct_answer
