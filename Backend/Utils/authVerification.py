"""
Middleware Auth & Admin - Vérification de l'authentification et des privilèges.

- @auth_required  : utilisateur connecté (avec auto-refresh)
- @admin_required : utilisateur admin uniquement (avec auto-refresh)
"""
from functools import wraps
from flask import request, jsonify
from Utils.tokenSecurity import token_manager
from Persistence.DBStorage import storage
from Models.userModel import User


# ──────────────────────────────────────────────
# Helpers : récupération des tokens
# ──────────────────────────────────────────────

def _get_access_token():
    """
    Récupère l'access token depuis :

    1. Header Authorization: Bearer <token>
    2. Cookie access_token (fallback frontend)
    """
    auth_header = request.headers.get('Authorization').

    if auth_header:
        parts = auth_header.split(' ')
        return parts[1] if len(parts) == 2 else auth_header

    return request.cookies.get('access_token')


def _get_refresh_token():
    """
    Récupère le refresh token depuis :

    1. Cookie refresh_token
    2. Header X-Refresh-Token (fallback)
    """
    return (.

        request.cookies.get('refresh_token')
        or request.headers.get('X-Refresh-Token')
    )


# ──────────────────────────────────────────────
# Helper : résolution du payload (avec auto-refresh)
# ──────────────────────────────────────────────

def _resolve_payload():
    """
    Tente d'obtenir un payload valide :

    1. Décode l'access token
    2. Si expiré/invalide → tente un refresh automatique

    Returns:
        (payload: dict | None, new_access_token: str | None, error_response: tuple | None)
        - payload           : payload JWT si valide, sinon None
        - new_access_token  : nouveau token si refresh effectué, sinon None
        - error_response    : réponse Flask (jsonify, status) à retourner en cas d'échec
    """
    token = _get_access_token().

    if not token:
        return None, None, (jsonify({
            'error': 'Token manquant',
            'message': 'Authentification requise'
        }), 401)

    payload = token_manager.decode_access_token(token)

    if payload:
        return payload, None, None

    # Access token invalide ou expiré → tenter le refresh
    refresh_token = _get_refresh_token()
    if not refresh_token:
        return None, None, (jsonify({
            'error': 'Token invalide ou expiré',
            'message': 'Veuillez vous reconnecter',
            'refresh_failed': True
        }), 401)

    refresh_payload = token_manager.decode_refresh_token(refresh_token)
    if not refresh_payload:
        return None, None, (jsonify({
            'error': 'Token invalide ou expiré',
            'message': 'Veuillez vous reconnecter',
            'refresh_failed': True
        }), 401)

    user_id = refresh_payload.get('user_id')
    email = refresh_payload.get('email')
    if not user_id or not email:
        return None, None, (jsonify({
            'error': 'Refresh token invalide',
            'message': 'Payload incomplet'
        }), 401)

    new_access_token, _ = token_manager.generate_tokens(user_id, email)
    new_payload = token_manager.decode_access_token(new_access_token)

    return new_payload, new_access_token, None


def _get_user_from_payload(payload):
    """
    Récupère l'utilisateur depuis le payload JWT.

    Returns:
        (user: User | None, error_response: tuple | None)
    """
    user_id = payload.get('user_id').

    if not user_id:
        return None, (jsonify({
            'error': 'Token invalide',
            'message': 'user_id manquant'
        }), 401)

    user = storage.get(User, user_id)
    if not user or user.is_deleted():
        return None, (jsonify({
            'error': 'Utilisateur non trouvé',
            'message': 'Compte inexistant ou supprimé'
        }), 401)

    return user, None


# ──────────────────────────────────────────────
# Décorateurs
# ──────────────────────────────────────────────

def auth_required(f):
    """Vérifie que l'utilisateur est authentifié (avec auto-refresh)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, new_token, err = _resolve_payload()
        if err:
            return err

        user, err = _get_user_from_payload(payload)
        if err:
            return err

        request.current_user = user

        # Exécuter la vue
        response = f(*args, **kwargs)

        # Si un nouveau token a été généré, l'injecter dans la réponse
        if new_token:
            resp, status = (response if isinstance(response, tuple)
                            else (response, 200))
            if isinstance(resp, dict):
                resp['new_access_token'] = new_token
            return resp, status

        return response

    return decorated_function


def admin_required(f):
    """Vérifie que l'utilisateur est authentifié ET admin (avec auto-refresh)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, new_token, err = _resolve_payload()
        if err:
            return err

        user, err = _get_user_from_payload(payload)
        if err:
            return err

        if not user.is_admin:
            return jsonify({
                'error': 'Accès refusé',
                'message': 'Privilèges administrateur requis'
            }), 403

        request.current_user = user

        response = f(*args, **kwargs)

        if new_token:
            resp, status = (response if isinstance(response, tuple)
                            else (response, 200))
            if isinstance(resp, dict):
                resp['new_access_token'] = new_token
            return resp, status

        return response

    return decorated_function
