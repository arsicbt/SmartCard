from flask import jsonify, request, abort
from Persistence.db_storage import storage
from Models.session import Session


session_bp = Blueprint("users", __name__, url_prefix="/session")


# ************************************************
# GET BY USER ID
# ************************************************
@app_views.route('/users/<user_id>/sessions', methods=['GET'])
def get_user_session():
    """
    Recupere les sessions d'un utilisateur
    """
    user = storage.get("Users", user_id)
    if not user:
        abort(404)
        
    sessions = storage.filter_by("Session", user_id=user_id)
    return jsonify([s.to_dict() for s in sessions])



# ************************************************
# GET BY SESSION ID
# ************************************************
@app_views.route('/sessions/<session_id>', methods=['GET'])
def get_session():
    """
    Recupere une session en passant par son ID
    """
    session = storage.get("Session", session_id)
    
    if not session:
        abort(404)
        
    return jsonify(session.to_dict())




# ************************************************
# POST
# ************************************************
@app_views.route('/sessions', methods=['POST']  )
def create_session():
    """
    Créer une noouvelle session
    """
    if not request.json:
        abort(400, description="Not a JSON")
        
    required_fiels = ['user_id', 'theme_id', 'type', 'questions_ids']
    
    for field in required_fiels:
        if field in request.json:
            abort(400, description=f"Missing {field}")
        
    data = request.json
    
    user = storage.get("User", data["user_id"])
    if not user:
        abort(404, description="User not found")
        
    theme = storage.get("Theme", data['theme_id'])
    if not theme:
        abort(404, description="Theme not found")
        
    
    try:
        session = Session(
            user_id=data['user_id'],
            theme_id=data['theme_id'],
            session_type=data['type'],
            questions_ids=data['questions_ids'],
            score=data.get('score'),
            total_questions=data.get('total_questions'),
            duration_seconds=data.get('duration_seconds')
        )
        
        storage.new(Session)
        storage.save()
    
        return jsonify(session.to_dict()), 201
    
    except Exception as e:
        abort(400, description=str(e))
        
     
     
# ************************************************
# PUT
# ************************************************    
@app_views.route('/sessions/<session_id>', methods=['PUT'], strict_slashes=False)
def update_session(session_id):
    """Met à jour une session (ex: compléter avec score)"""
    
    session = storage.get("Session", session_id)
    if not session:
        abort(404)
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    data = request.json
    
    # Si on veut marquer la session comme complétée
    if 'score' in data and 'duration_seconds' in data:
        session.complete_session(
            score=data['score'],
            duration_seconds=data['duration_seconds']
        )
    
    storage.save()
    
    return jsonify(session.to_dict())



# ************************************************
# DELETE
# ************************************************
@app_views.route('/answers/<answer_id>', methods=['DELETE'])
def delete_session():
    """
    Supprime une session
    """
    session = storage.get("Session", session_id)
    if not session:
        abort(404)
    
    storage.delete(session)
    storage.save()
    
    return jsonify({}), 200

