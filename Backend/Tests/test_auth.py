import pytest
import sys
import os

# Ajustement du chemin pour s'assurer que le dossier parent (Backend) est accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importations basées exactement sur tes classes et instances réelles
from Utils.passwordSecurity import PasswordManager
from Utils.inputSecurity import InputValidator
from Utils.tokenSecurity import token_manager


# ──────────────────────────────────────────────────────────────
# 🔐 TESTS : GESTION DES MOTS DE PASSE (PasswordManager)
# ──────────────────────────────────────────────────────────────

def test_password_manager_hashing():
    """
    Vérifie que PasswordManager hache correctement un mot de passe avec du sel (bcrypt)
    et que la vérification de correspondance fonctionne.
    """
    raw_password = "MonMotDePasseSecurise123!"
    
    # Génération du hash
    hashed = PasswordManager.hash_password(raw_password)
    
    # Assertions de sécurité de base
    assert hashed != raw_password
    assert isinstance(hashed, str)
    assert len(hashed) > 0

    # Vérification avec le bon mot de passe
    assert PasswordManager.verify_password(raw_password, hashed) is True
    
    # Vérification avec un mauvais mot de passe
    assert PasswordManager.verify_password("MauvaisMotDePasse!", hashed) is False


# ──────────────────────────────────────────────────────────────
# 🛠️ TESTS : VALIDATION & NETTOYAGE DES ENTRÉES (InputValidator)
# ──────────────────────────────────────────────────────────────

def test_input_validator_email():
    """Vérifie les règles de validation des formats d'emails (regex)."""
    # Cas d'emails valides
    valid_status, error_msg = InputValidator.validate_email("user@example.com")
    assert valid_status is True
    assert error_msg is None

    # Cas d'emails invalides
    assert InputValidator.validate_email("invalid-email")[0] is False
    assert InputValidator.validate_email("user@.com")[0] is False
    assert InputValidator.validate_email("")[0] is False


def test_input_validator_password_complexity():
    """Vérifie l'application stricte des critères de complexité des mots de passe."""
    # Mot de passe valide (Min 8 caractères, 1 Maj, 1 Min, 1 Chiffre, 1 Spécial)
    valid_status, error_msg = InputValidator.validate_password("Secure123!")
    assert valid_status is True
    assert error_msg is None

    # Échecs sur critères spécifiques
    assert InputValidator.validate_password("short")[0] is False             # Trop court
    assert InputValidator.validate_password("sansmajuscule1!")[0] is False    # Pas de majuscule
    assert InputValidator.validate_password("SANSMAJUSCULE1!")[0] is False    # Pas de minuscule
    assert InputValidator.validate_password("SecureLetters!")[0] is False     # Pas de chiffre
    assert InputValidator.validate_password("SecurePassword123")[0] is False  # Pas de caractère spécial


def test_input_validator_sanitize_string():
    """Vérifie le nettoyage des chaînes de caractères contre les octets de contrôle."""
    dangerous_string = "Texte\x00normal avec\x1f caractères cachés."
    cleaned = InputValidator.sanitize_string(dangerous_string)
    
    assert "\x00" not in cleaned
    assert "\x1f" not in cleaned
    assert cleaned == "Textenormal avec caractères cachés."


# ──────────────────────────────────────────────────────────────
# 🎟️ TESTS : CHAÎNE DE JETONS JWT (token_manager)
# ──────────────────────────────────────────────────────────────

def test_token_manager_generation_and_decoding():
    """
    Vérifie la création conjointe d'un Access Token et d'un Refresh Token,
    ainsi que leur décodage et la validation de leur type de charge utile.
    """
    user_id = "user_uuid_123"
    email = "test@smartcard.com"

    # Génération des deux jetons via l'instance token_manager
    access_token, refresh_token = token_manager.generate_tokens(user_id, email)

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)

    # Décodage et vérification de l'Access Token (30 min)
    access_payload = token_manager.decode_access_token(access_token)
    assert access_payload is not None
    assert access_payload["user_id"] == user_id
    assert access_payload["email"] == email
    assert access_payload["type"] == "access"

    # Décodage et vérification du Refresh Token (7 jours)
    refresh_payload = token_manager.decode_refresh_token(refresh_token)
    assert refresh_payload is not None
    assert refresh_payload["user_id"] == user_id
    assert refresh_payload["type"] == "refresh"


def test_token_manager_invalid_or_expired():
    """Vérifie que le décodeur rejette correctement les jetons corrompus."""
    bad_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.payload"
    
    assert token_manager.decode_access_token(bad_token) is None
    assert token_manager.decode_refresh_token(bad_token) is None
