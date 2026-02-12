from flask import Blueprint, jsonify, request, abort
from Utils.passwordSecurity import PasswordManager
from Utils.inputSecurity import InputValidator
from Persistence.DBStorage import storage
from Models.userModel import User
from Utils.authVerification import auth_required, admin_required
import bcrypt


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# ************************************************
# GET ALl
# ************************************************
@admin_required
@users_bp.route('/', methods=['GET'])
def get_users():
    """REcupere tous les utilisateur"""
    users = storage.all(User)
    # Serialization
    return jsonify([user.to_dict() for user in users.values()])



# ************************************************
# GET BY ID
# ************************************************
@admin_required
@users_bp.route('/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Recupere l'utilisateur via son id"""
    user = storage.get(User, user_id)
    
    if not user:
        abort(404)
    
    return jsonify(user.to_dict())



# ************************************************
# POST
# ************************************************
@auth_required
@users_bp.route('/', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur"""
    if not request.json:
        abort(400, description="Not a JSON")
        
    if 'email' not in request.json:
        abort(400, description="Missing email")
        
    if 'password' not in request.json:
        abort(400, description="Missing password")
    
    
    data = request.json
    
    is_valid, error = InputValidator.validate_email(data['email'])
    if not is_valid:
        abort(400, description=error)

    is_valid, error = InputValidator.validate_password(data['password'])
    if not is_valid:
        abort(400, description=error)

    if storage.filter_by(User, email=data['email']):
        abort(400, description="Email already exists")

    hashed = PasswordManager.hash_password(data['password'])
    
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=hashed,
            name=data['name']
        )
        
        storage.new(user)
        storage.save()
    
        return jsonify(user.to_dict()), 201
    
    except Exception as e:
        abort(400, description=str(e))



# ************************************************
# PUT
# ************************************************
@auth_required
@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Mets à jour les données utilisateurs
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404)
        
    if not request.json: 
        abort(400, description="Not a JSON")
        
    data = request.json
          
    ignored_keys = ['id', 'created_at', 'updated_at', 'deleted_at', 'password_hash']
    
    for k, v in data.items():
        if k not in ignored_keys and hasattr(user, k):
            setattr(user, k, v)
            
    user.update_timestamp()
    storage.save()
    
    return jsonify(user.to_dict())



# ************************************************
# DELETE
# ************************************************
@admin_required
@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Supprime (soft delete) l'utilisateur 
    """

    user = storage.get(User, user_id)
    
    if not user:
        abort(404)
        
    storage.delete(user)
    storage.save()
    
    return jsonify({}, 200)