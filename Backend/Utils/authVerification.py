"""
Middleware Auth & Admin - Vérification de l'authentification et des privilèges

- @auth_required : utilisateur connecté
- @admin_required : utilisateur admin uniquement
"""

from functools import wraps
from flask import request, jsonify
from Utils.tokenSecurity import TokenManager
from Persistence.DBStorage import storage


def _get_token_from_request():
    """
    Récupère le token JWT depuis :
    1. Header Authorization: Bearer <token>
    2. Cookie access_token (frontend JS)

    Returns:
        token (str) ou None
    """
    token = None

    # 1. Header Authorization
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        except IndexError:
            return None

    # 2. Cookie (fallback)
    if not token:
        token = request.cookies.get('access_token')

    return token


def auth_required(f):
    """
    Décorateur pour vérifier que l'utilisateur est authentifié
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Récupérer le token
        token = _get_token_from_request()

        if not token:
            return jsonify({
                'error': 'Token manquant',
                'message': 'Authentification requise'
            }), 401

        # 2. Vérifier le token
        payload = TokenManager.verify_token(token)
        if not payload:
            return jsonify({
                'error': 'Token invalide ou expiré',
                'message': 'Veuillez vous reconnecter'
            }), 401

        # 3. Récupérer l'utilisateur
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Token invalide',
                'message': 'user_id manquant'
            }), 401

        user = storage.get('User', user_id)

        if not user or user.is_deleted():
            return jsonify({
                'error': 'Utilisateur non trouvé',
                'message': 'Compte inexistant ou supprimé'
            }), 401

        # 4. Injecter l'utilisateur dans la requête
        request.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Décorateur pour vérifier que l'utilisateur est admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Récupérer le token
        token = _get_token_from_request()

        if not token:
            return jsonify({
                'error': 'Token manquant',
                'message': 'Authentification requise'
            }), 401

        # 2. Vérifier le token
        payload = TokenManager.verify_token(token)
        if not payload:
            return jsonify({
                'error': 'Token invalide ou expiré',
                'message': 'Veuillez vous reconnecter'
            }), 401

        # 3. Récupérer l'utilisateur
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Token invalide',
                'message': 'user_id manquant'
            }), 401

        user = storage.get('User', user_id)

        if not user or user.is_deleted():
            return jsonify({
                'error': 'Utilisateur non trouvé',
                'message': 'Compte inexistant ou supprimé'
            }), 401

        # 4. Vérifier privilèges admin
        if not user.is_admin:
            return jsonify({
                'error': 'Accès refusé',
                'message': 'Privilèges administrateur requis'
            }), 403

        # 5. Injecter l'utilisateur
        request.current_user = user

        return f(*args, **kwargs)

    return decorated_function
