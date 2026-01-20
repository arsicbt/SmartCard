import re
from models.user import User
from storage.memory_storage import MemoryStorage


class UserService:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    # --- C R E A T E   S E C T I O N  ------------------
    def create_user(self, data: dict) -> User:
        self._validate_creation_data(data)

        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
        )

        self.storage.save(user)
        return user


    # --- U P D A T E  S E C T I O N --------------------
    def update_user(self, current_user: User, target_user_id: str, data: dict) -> User:
        user = self.storage.get(target_user_id)
        if not user:
            raise ValueError("User not found")

        if current_user.id != user.id and not current_user.is_admin:
            raise PermissionError("Forbidden")

        allowed_fields = self._allowed_update_fields(current_user)
        filtered_data = {
            k: v for k, v in data.items() if k in allowed_fields
        }

        self._validate_update_data(filtered_data)

        user.update_fields(filtered_data)
        self.storage.save(user)
        return user


    # --- D E L E T E   S E C T I O N -------------------
    def delete_user(self, current_user: User, target_user_id: str):
        if not current_user.is_admin:
            raise PermissionError("Admin only")

        self.storage.delete(target_user_id)


    # --- V A L I D A T I O N ---------------------------
    def _validate_creation_data(self, data: dict):
        required = ["first_name", "last_name", "email", "password"]
        for field in required:
            if field not in data or not data[field].strip():
                raise ValueError(f"{field} is required")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            raise ValueError("Invalid email format")

    def _validate_update_data(self, data: dict):
        if "email" in data:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError("Invalid email format")

    def _allowed_update_fields(self, user: User):
        if user.is_admin:
            return {"first_name", "last_name", "email", "is_admin"}
        return {"first_name", "last_name"}
