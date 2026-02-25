from flask import Blueprint, request, jsonify, make_response
from Utils.passwordSecurity import PasswordManager
from Utils.tokenSecurity import token_manager
from Utils.authVerification import auth_required, admin_required
from Persistence.DBStorage import storage
from Models.userModel import User


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ********************************************************
# LOGIN
# ********************************************************
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authentifie un utilisateur et retourne un JWT"""
    if not request.json:
        return jsonify({'error': 'Not a JSON'}), 400

    email    = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    users = storage.filter_by(User, email=email)
    if not users:
        return jsonify({'error': 'Identifiants invalides'}), 401

    user = users[0]

    if user.is_deleted():
        return jsonify({'error': 'Compte supprimé'}), 401

    if not PasswordManager.verify_password(password, user.password):
        return jsonify({'error': 'Identifiants invalides'}), 401

    # Générer access + refresh token
    access_token, refresh_token = token_manager.generate_tokens(
        user_id=user.id,
        email=user.email
    )

    response = make_response(jsonify({
        'message': 'Connexion réussie',
        'token':   access_token,
        'user':    user.to_dict()
    }))

    # Stocker le refresh token dans un cookie httpOnly
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        samesite='Strict',
        secure=False,  # True en prod (HTTPS)
        max_age=7 * 24 * 3600  # 7 jours
    )

    return response, 200


# ********************************************************
# LOGOUT
# ********************************************************
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Supprime les cookies JWT"""
    response = make_response(jsonify({'message': 'Déconnexion réussie'}))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response, 200


# ********************************************************
# USER CONNECTÉ
# ********************************************************
@auth_bp.route('/me', methods=['GET'])
@auth_required
def me():
    """Retourne l'utilisateur connecté"""
    return jsonify(request.current_user.to_dict()), 200


# ********************************************************
# CRÉER UN ADMIN
# ********************************************************
@auth_bp.route('/admin', methods=['POST'])
@admin_required
def create_admin():
    """Crée un utilisateur admin (réservé aux admins)"""
    if not request.json:
        return jsonify({'error': 'Not a JSON'}), 400

    data = request.json
    required = ['email', 'password', 'first_name', 'last_name', 'name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400

    if storage.filter_by(User, email=data['email']):
        return jsonify({'error': 'Email déjà utilisé'}), 400

    admin = User(
        email=data['email'],
        password=PasswordManager.hash_password(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        name=data['name'],
        is_admin=True
    )

    storage.new(admin)
    storage.save()

    return jsonify(admin.to_dict()), 201