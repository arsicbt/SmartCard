"""Users paths.

Les routes valident la requête HTTP puis délèguent la logique métier au
service `UserService` (Services/usersServices.py). Aucune logique métier
complexe ne doit subsister directement dans ce fichier.
"""

from flask import Blueprint, jsonify, request, abort
from Persistence.DBStorage import storage
from Models.userModel import User
from Services.usersServices import UserService
from Utils.authVerification import auth_required, admin_required


users_bp = Blueprint("users", __name__, url_prefix="/api/users")

# Service métier (logique pure, sans dépendance HTTP)
user_service = UserService(storage)


# ************************************************
# GET ALl
# ************************************************
@users_bp.route('/', methods=['GET'])
@admin_required
def get_users():
    """Récupère tous les utilisateurs (réservé aux admins)."""
    users = user_service.get_all_users()
    return jsonify([user.to_dict() for user in users])


# ************************************************
# GET BY ID
# ************************************************
@users_bp.route('/<user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """Récupère l'utilisateur via son id (réservé aux admins)."""
    user = user_service.get_user_by_id(user_id)

    if not user:
        abort(404)

    return jsonify(user.to_dict())


# ************************************************
# POST
# ************************************************
@users_bp.route('/', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur."""
    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json

    # Validation simple de présence des champs obligatoires (reste dans la route)
    required = ['first_name', 'last_name', 'email', 'password']
    for field in required:
        if field not in data:
            abort(400, description=f"Missing {field}")

    user, error = user_service.create_user(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password'],
        name=data.get('name')
    )

    if error:
        abort(400, description=error)

    return jsonify(user.to_dict()), 201


# ************************************************
# PUT
# ************************************************
@users_bp.route('/<user_id>', methods=['PUT'])
@auth_required
def update_user(user_id):
    """Met à jour les données d'un utilisateur."""
    if not request.json:
        abort(400, description="Not a JSON")

    user, error = user_service.update_user(user_id, request.json)

    if error:
        abort(404, description=error)

    return jsonify(user.to_dict())


# ************************************************
# DELETE
# ************************************************
@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Supprime (soft delete) l'utilisateur (réservé aux admins)."""
    success, error = user_service.delete_user(user_id)

    if not success:
        abort(404, description=error)

    return jsonify({"message": "User deleted"}), 200
