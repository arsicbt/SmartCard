from .coreModel import CoreModel


class DocumentModel(CoreModel):
    # ATTRIBUT ------------------------
    def __init__(self, text_content):
        super().__init__():
        self.text_content = text_content
    
    # SERIALIZATION -------------------
    def to_dict():
        data = super().to_dict()
        data.update({
            'text_content': self.text_content
        })
        
        return data
