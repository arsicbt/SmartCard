from Models.CoreModel import CoreModel
from Models.tablesSchema import User as UserDB
from Utils.passwordSecurity import PasswordManager
from Utils.tokenSecurity import TokenManager
from Utils.inputSecurity import InputValidator

class User(BaseModel, UserDB):
    
    def set_password(self, password: str):
        """
        Définit le mot de passe (hash automatique)
        
        SÉCURITÉ : Validation + hash bcrypt
        """
        is_valid, error = InputValidator.validate_password(password)
        if not is_valid:
            raise ValueError(error)
        
        self.password = PasswordManager.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe"""
        return PasswordManager.verify_password(password, self.password)
    
    def generate_token(self) -> str:
        """Génère un JWT pour l'utilisateur"""
        return TokenManager.create_access_token(self.id, self.email)
    
    def to_dict(self, include_private=False):
        """
        Export sécurisé
        
        Args:
            include_private: Inclure données sensibles (email verification token)
        """
        data = super().to_dict()
        
        # Toujours supprimer le password
        data.pop('password', None)
        
        if not include_private:
            # Supprime tokens de vérification
            data.pop('verification_token', None)
        
        return data
