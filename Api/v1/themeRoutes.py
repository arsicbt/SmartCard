from flask import jsonify, request, abort
from API.v1.views import app_views
from .Utils import hash_password
from Persistence.db_storage import storage
from Models.user import User
import bcrypt



# ************************************************
# GET ALl
# ************************************************
@app_views.route('/themes', methods=['GET'])
def get_themes():
    """
    Récupère tous les thèmes
    """
    themes = storage.all("Theme")
    return jsonify([theme.to_dict() for theme in themes.values()])



# ************************************************
# GET BY ID 
# ************************************************
@app_views.route('/themes/<theme_id>', methods=['GET'])
def get_theme(theme_id):
    """
    Récupère un thème par ID
    """
    theme = storage.get("Theme", theme_id)
    
    if not theme:
        abort(404)
    
    return jsonify(theme.to_dict())



# ************************************************
# GET ALL
# ************************************************
@app_views.route('/themes', methods=['GET'], strict_slashes=False)
def get_themes():
    """
    Récupère tous les thèmes
    """
    themes = storage.all("Theme")
    return jsonify([theme.to_dict() for theme in themes.values()])



# ************************************************
# POST 
# ************************************************
@app_views.route('/themes', methods=['POST'], strict_slashes=False)
def create_theme():
    """
    Crée un nouveau thème
    """
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    required_fields = ['name', 'keywords', 'user_id']
    for field in required_fields:
        if field not in request.json:
            abort(400, description=f"Missing {field}")
    
    data = request.json
    
    # Vérifier que l'utilisateur existe
    user = storage.get("User", data['user_id'])
    if not user:
        abort(404, description="User not found")
    
    try:
        theme = Theme(
            name=data['name'],
            keywords=data['keywords'],
            user_id=data['user_id'],
            description=data.get('description'),
            is_public=data.get('is_public', False)
        )
        
        storage.new(theme)
        storage.save()
        
        return jsonify(theme.to_dict()), 201
        
    except Exception as e:
        abort(400, description=str(e))
        
    

# ************************************************
# PUT
# ************************************************
@app_views.route('/themes/<theme_id>', methods=['PUT'], strict_slashes=False)
def update_theme(theme_id):
    """
    Met à jour un thème
    """
    
    theme = storage.get("Theme", theme_id)
    if not theme:
        abort(404)
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    data = request.json
    ignore_keys = ['id', 'user_id', 'created_at', 'updated_at', 'deleted_at']
    
    for key, value in data.items():
        if key not in ignore_keys and hasattr(theme, key):
            setattr(theme, key, value)
    
    theme.update_timestamp()
    storage.save()
    
    return jsonify(theme.to_dict())



# ************************************************
# DELETE
# ************************************************
@app_views.route('/themes/<theme_id>', methods=['DELETE'], strict_slashes=False)
def delete_theme(theme_id):
    """
    Supprime un thème
    """
    
    theme = storage.get("Theme", theme_id)
    if not theme:
        abort(404)
    
    storage.delete(theme)
    storage.save()
    
    return jsonify({}), 200