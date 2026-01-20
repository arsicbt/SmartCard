import uuid
from datetime import datetime


class CoreModel:
    
    # --- A T T R I B U T S ---------------------------------
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


    # --- P A T C H -----------------------------------------
    def save(self):
        """Update timestamp"""
        self.updated_at = datetime.utcnow()

    def update(self, **kwargs):
        """
        Update allowed attributes only.
        Child classes should override __allowed_fields__
        """
        allowed = getattr(self, "__allowed_fields__", [])
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.save()


    # --- S E R I A L I Z A T I O N -------------------------
    def to_dict(self):
        """Serialize base attributes"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
