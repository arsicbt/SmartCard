"""
Middleware Auth & Admin - Vérification de l'authentification et des privilèges

- @auth_required : utilisateur connecté (avec auto-refresh)
- @admin_required : utilisateur admin uniquement (avec auto-refresh)
"""

from functools import wraps
from flask import request, jsonify
from Utils.tokenSecurity import TokenManager
from Persistence.DBStorage import storage
from Models.userModel import User


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


def _get_refresh_token_from_request():
    """
    Récupère le refresh token depuis :
    1. Cookie refresh_token
    2. Header X-Refresh-Token

    Returns:
        refresh_token (str) ou None
    """
    # 1. Cookie
    refresh_token = request.cookies.get('refresh_token')
    
    # 2. Header (fallback)
    if not refresh_token:
        refresh_token = request.headers.get('X-Refresh-Token')
    
    return refresh_token


def _try_refresh_token():
    """
    Tente de rafraîchir l'access token avec le refresh token
    
    Returns:
        tuple: (success: bool, new_access_token: str|None, error_message: str|None)
    """
    refresh_token = _get_refresh_token_from_request()
    
    if not refresh_token:
        return False, None, "Refresh token manquant"
    
    # Décoder le refresh token
    payload = TokenManager.decode_refresh_token(refresh_token)
    
    if not payload:
        return False, None, "Refresh token invalide ou expiré"
    
    # Vérifier que c'est bien un refresh token
    if payload.get('type') != 'refresh':
        return False, None, "Token invalide"
    
    user_id = payload.get('user_id')
    email = payload.get('email')
    
    if not user_id or not email:
        return False, None, "Payload incomplet"
    
    # Générer un nouveau access token
    new_access_token, _ = TokenManager.generate_tokens(user_id, email)
    
    return True, new_access_token, None


def auth_required(f):
    """
    Décorateur pour vérifier que l'utilisateur est authentifié
    Gère automatiquement le refresh du token si expiré
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
        payload = TokenManager.decode_access_token(token)
        
        # AUTO-REFRESH : Si le token est expiré, essayer de le rafraîchir
        if not payload:
            success, new_token, error = _try_refresh_token()
            
            if success:
                # Token rafraîchi avec succès
                token = new_token
                payload = TokenManager.decode_access_token(token)
                
                # Retourner le nouveau token dans le header de réponse
                response = f(*args, **kwargs)
                if isinstance(response, tuple):
                    resp, status = response[0], response[1] if len(response) > 1 else 200
                else:
                    resp, status = response, 200
                
                # Ajouter le nouveau token dans la réponse
                if isinstance(resp, dict):
                    resp['new_access_token'] = new_token
                
                return resp, status
            else:
                # Impossible de rafraîchir
                return jsonify({
                    'error': 'Token invalide ou expiré',
                    'message': 'Veuillez vous reconnecter',
                    'refresh_failed': True
                }), 401

        # 3. Récupérer l'utilisateur
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Token invalide',
                'message': 'user_id manquant'
            }), 401

        user = storage.get(User, user_id)

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
    Gère automatiquement le refresh du token si expiré
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
        payload = TokenManager.decode_access_token(token)
        
        # ⭐ AUTO-REFRESH : Si le token est expiré, essayer de le rafraîchir
        if not payload:
            success, new_token, error = _try_refresh_token()
            
            if success:
                # Token rafraîchi avec succès
                token = new_token
                payload = TokenManager.decode_access_token(token)
                
                # Continuer avec le nouveau token
                # (le reste du code vérifiera l'admin)
            else:
                # Impossible de rafraîchir
                return jsonify({
                    'error': 'Token invalide ou expiré',
                    'message': 'Veuillez vous reconnecter',
                    'refresh_failed': True
                }), 401

        # 3. Récupérer l'utilisateur
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Token invalide',
                'message': 'user_id manquant'
            }), 401

        user = storage.get(User, user_id)

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