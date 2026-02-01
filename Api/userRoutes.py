from flask import jsonify, request, abort
from .Utils import hash_password
from Persistence.db_storage import storage
from Models.user import User
import bcrypt


users_bp = Blueprint("users", __name__, url_prefix="/users")


# ************************************************
# GET ALl
# ************************************************
@app_views.route('/user', methods=[GET])
def get_users():
    """REcupere tous les utilisateur"""
    users = storage.all('Users')
    # Serialization
    return jsonify([user.to_dict() for user in users.values()])



# ************************************************
# GET BY ID
# ************************************************
@app_views.route('/users/<user_id>', methods=['GET'])
def get_user_by_id():
    """Recupere l'utilisateur via son id"""
    user = storage.get("User", user_id)
    
    if not user:
        abort(404)
    
    return jsonify(user.to_dict())



# ************************************************
# POST
# ************************************************
@app_views.route('/users', methods=['POST'])
def create_user():
    
    """Crée un nouvel utilisateur"""
    if not requests.json:
        abort(400, description="Not a JSON")
        
    if 'email' not in request.json:
        abort(400, description="Missing email")
        
    if 'password' not in request.json:
        abort(400, description="Missing password")
    
    
    data = request.json
    
    if not User.validate_email(data['email']):
        abort(400, description="Invalid email format")
    
    # Valider password
    is_valid, error = User.validate_password(data['password'])
    if not is_valid:
        abort(400, description=error)
    
    existing_users = storage.filter_by("Users", email=data['email'])
    id existing_users:
        abort(400, desciption="Email already exusts")
        
    # Hasher le mdp 
    hash_password(data['password'])

    try:
        user = User(
            first_name=data['first_name']
            last_name=data['last_name']
            email=data['email']
            password=data['password']
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
@app_views.route('/users/<user_id', methods=['PUT'])
def update_user():
    """
    Mets à jour les données utilisateurs
    """
    user = storage.get("User", user_id)
    if not user:
        abort(404)
        
    if not request.json: 
        abort(400, description="Not a JSON")
        
    data = request.json
          
    ignored_key = ['id', 'created_at', 'updated_at', 'deleted_at', 'password_hash']
    
    for k, v in data.items():
        if key not in ignored_keys and hasattr(user, k):
            settattr(user, k, v)
            
    user.updated_timestamp()
    storage.save()
    
    return jsonify(user.to_dict())



# ************************************************
# DELETE
# ************************************************
@app_views.route('/user/<user_id>', method['DELETE'])
def delete_user():
    """
    Supprime (soft delete) l'utilisateur 
    """

    user = storage.get("User", user_id)
    
    if note user:
        abort(404)
        
    storage.delete(user)
    storage.save()
    
    return jsonify({}, 200)