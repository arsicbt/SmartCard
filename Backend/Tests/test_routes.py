"""Tests d'intégration des routes API.

Contrairement à des tests "flous" qui acceptent plusieurs codes HTTP à la
fois, chaque test ici vérifie UN comportement précis attendu, sur une vraie
base de données de test (SQLite en mémoire, voir conftest.py). C'est ce qui
permet de détecter une régression si une route casse.
"""
import uuid


# ──────────────────────────────────────────────────────────────
# 🔐 REGISTER
# ──────────────────────────────────────────────────────────────

def test_register_creates_user(client):
    """Un enregistrement avec des données valides doit renvoyer 201
    et l'utilisateur créé (sans mot de passe en clair)."""
    payload = {
        "email": f"new_{uuid.uuid4().hex[:8]}@smartcard.com",
        "password": "SecurePassword123!",
        "first_name": "Alice",
        "last_name": "Dupont",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == payload["email"]
    assert "password" not in data


def test_register_missing_field_returns_400(client):
    """Un champ obligatoire manquant doit être rejeté avec 400."""
    payload = {
        "email": "incomplet@smartcard.com",
        "password": "SecurePassword123!",
        # first_name et last_name manquants
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400


def test_register_duplicate_email_returns_409(client, registered_user):
    """Réutiliser un email déjà inscrit doit être refusé avec 409."""
    payload = {
        "email": registered_user["email"],
        "password": "AutreMotDePasse123!",
        "first_name": "Bob",
        "last_name": "Martin",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 409


# ──────────────────────────────────────────────────────────────
# 🔑 LOGIN
# ──────────────────────────────────────────────────────────────

def test_login_success_returns_token(client, registered_user):
    """Des identifiants corrects doivent renvoyer 200 et un token JWT."""
    response = client.post("/api/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["user"]["email"] == registered_user["email"]


def test_login_wrong_password_returns_401(client, registered_user):
    """Un mauvais mot de passe doit être refusé avec 401, jamais 200."""
    response = client.post("/api/auth/login", json={
        "email": registered_user["email"],
        "password": "MauvaisMotDePasse!",
    })

    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    """Un email inexistant doit renvoyer 401 (et pas 404, pour ne pas
    révéler si un compte existe ou non — bonne pratique sécurité)."""
    response = client.post("/api/auth/login", json={
        "email": "inconnu@smartcard.com",
        "password": "PeuImporte123!",
    })

    assert response.status_code == 401


# ──────────────────────────────────────────────────────────────
# 🌐 ROUTES PROTÉGÉES : /api/questions
# ──────────────────────────────────────────────────────────────

def test_questions_without_token_returns_401(client):
    """Une route protégée par @auth_required doit refuser une requête
    sans token, avec 401 exactement (pas 404, pas 200)."""
    response = client.get("/api/questions/")

    assert response.status_code == 401


def test_questions_with_valid_token_returns_200(client, auth_headers):
    """Avec un token valide, la route doit répondre 200 et renvoyer
    une liste JSON (vide au départ, aucune question créée)."""
    response = client.get("/api/questions/", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == []


# ──────────────────────────────────────────────────────────────
# 🎟️ CRÉATION DE SESSION
# ──────────────────────────────────────────────────────────────

def test_create_session_without_token_returns_401(client):
    """Créer une session sans être authentifié doit être refusé."""
    response = client.post("/api/sessions/", json={
        "user_id": "peu-importe",
        "type": "QUIZ",
        "questions_ids": ["q1"],
    })

    assert response.status_code == 401


def test_create_session_missing_field_returns_400(client, auth_headers):
    """Un champ obligatoire manquant (ici questions_ids) doit être
    rejeté avec 400, même si l'utilisateur est authentifié."""
    response = client.post("/api/sessions/", json={
        "user_id": "peu-importe",
        "type": "QUIZ",
    }, headers=auth_headers)

    assert response.status_code == 400


def test_create_session_unknown_user_returns_404(client, auth_headers):
    """Si le user_id fourni dans le corps de la requête n'existe pas
    en base, l'API doit renvoyer 404 (et non planter en 500)."""
    response = client.post("/api/sessions/", json={
        "user_id": "id-qui-nexiste-pas",
        "type": "QUIZ",
        "questions_ids": ["q1", "q2"],
    }, headers=auth_headers)

    assert response.status_code == 404


def test_create_session_invalid_type_returns_400(client, auth_headers, registered_user):
    """Un type de session hors de la liste autorisée (QUIZ, FLASHCARD)
    doit être rejeté avec 400."""
    response = client.post("/api/sessions/", json={
        "user_id": registered_user["id"],
        "type": "PAS_UN_TYPE_VALIDE",
        "questions_ids": ["q1"],
    }, headers=auth_headers)

    assert response.status_code == 400
