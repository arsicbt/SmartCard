import re
from .coreModel import CoreModel


class User(CoreModel):

    __allowed_fields__ = ["first_name", "last_name", "email", "password"]
    
    # --- A T T R I B U T S ---------------------------------
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin

        self.validate()

    # --- H E L P E R ----------------------------------------
    def validate(self):
        """Validate user data"""
        errors = {}

        if not self.first_name or not self.first_name.strip():
            errors["first_name"] = "First name is required"

        if not self.last_name or not self.last_name.strip():
            errors["last_name"] = "Last name is required"

        if not self.email or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            errors["email"] = "Invalid email"

        if not self.password or len(self.password) < 8:
            errors["password"] = "Password too short"

        if errors:
            raise ValueError(errors)

    
    def to_dict(self):
        """Hide sensitive data to secure the update"""
        data = super().to_dict()
        data.update({
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin
        })
        return data
