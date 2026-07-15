import os
import sys
import uuid

# 1. Base de test : SQLite en mémoire (recréée à zéro à chaque run de tests)
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret-key')

# 2. Rendre le dossier Backend importable (pour "from app import app", etc.)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest


@pytest.fixture(scope="session")
def flask_app():
    """Instancie l'app Flask une seule fois pour toute la session de tests."""
    from app import app as _app
    _app.config.update(TESTING=True)
    return _app


@pytest.fixture()
def client(flask_app):
    """Client de test Flask : simule des requêtes HTTP sans lancer de serveur."""
    return flask_app.test_client()


@pytest.fixture()
def registered_user(client):
    """Crée un utilisateur unique via l'API /api/auth/register et renvoie
    ses identifiants (utile pour les tests de login/routes protégées)."""
    email = f"user_{uuid.uuid4().hex[:8]}@smartcard.com"
    password = "SecurePassword123!"

    payload = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "User",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.get_json()

    body = response.get_json()
    return {"email": email, "password": password, "id": body["id"]}


@pytest.fixture()
def auth_headers(client, registered_user):
    """Connecte l'utilisateur de test et renvoie le header Authorization
    prêt à être injecté dans une requête protégée."""
    response = client.post("/api/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert response.status_code == 200, response.get_json()

    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}