from flask import Blueprint, jsonify, request, abort
from Models.sessionModel import Session
from Models.tablesSchema import SessionType
from Models.userModel import User
from Models.themeModel import Theme
from Utils.authVerification import auth_required, admin_required
from Persistence.DBStorage import storage
import os


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"pdf"}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

session_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


# ************************************************
# GET SESSIONS BY USER ID
# ************************************************
@admin_required
@session_bp.route('/user/<user_id>', methods=['GET'])
def get_user_sessions(user_id):
    
    """
    Récupère les sessions d'un utilisateur
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404, description="User not found")
        
    sessions = storage.filter_by(Session, user_id=user_id)
    return jsonify([s.to_dict() for s in sessions]), 200



# ************************************************
# GET SESSION BY ID
# ************************************************
@admin_required
@session_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Récupère une session en passant par son ID
    """
    session = storage.get(Session, session_id)
    
    if not session:
        abort(404, description="Session not found")
        
    return jsonify(session.to_dict()), 200



# ************************************************
# POST - CREATE SESSION
# ************************************************
@auth_required
@session_bp.route('/', methods=['POST'])
def create_session():
    """
    Crée une nouvelle session
    """
    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.json

    # Champs obligatoires
    required_fields = ['user_id', 'type', 'questions_ids']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    # Vérifier que l'utilisateur existe
    user = storage.get(User, data["user_id"])
    if not user:
        abort(404, description="User not found")

    # Vérifier que le thème existe (optionnel)
    theme_id = data.get("theme_id")
    if theme_id:
        theme = storage.get(Theme, theme_id)
        if not theme:
            abort(404, description="Theme not found")

    # Vérifier que le type est valide
    allowed_types = ["QUIZ", "FLASHCARD"]
    session_type = data["type"].upper()
    if session_type not in allowed_types:
        abort(400, description=f"Invalid session type: {data['type']}")

    # Vérifier que questions_ids est une liste non vide
    questions_ids = data["questions_ids"]
    if not isinstance(questions_ids, list) or not questions_ids:
        abort(400, description="questions_ids must be a non-empty list")

    try:
        # Création de la session
        session = Session(
            user_id=data["user_id"],
            theme_id=theme_id,
            type=session_type,
            questions_ids=questions_ids,
            questions_count=len(questions_ids),
            score=data.get("score"),
            max_score=data.get("max_score")
        )

        storage.new(session)
        storage.save()

        return jsonify(session.to_dict()), 201

    except Exception as e:
        # Rollback propre en cas d'erreur
        storage.rollback()
        abort(400, description=f"Error creating session: {str(e)}")
     
     
     
# ************************************************
# PUT - UPDATE SESSION
# ************************************************
@auth_required    
@session_bp.route('/<session_id>', methods=['PUT'])
def update_session(session_id):
    """Met à jour une session (ex: compléter avec score)"""
    
    session = storage.get(Session, session_id)
    if not session:
        abort(404, description="Session not found")
    
    if not request.is_json:
        abort(400, description="Not a JSON")
    
    data = request.json
    
    # Si on veut marquer la session comme complétée
    if 'score' in data and 'max_score' in data:
        session.complete_session(
            score=data['score'],
            max_score=data['max_score']
        )
    
    storage.save()
    
    return jsonify(session.to_dict()), 200



# ************************************************
# DELETE - DELETE SESSION
# ************************************************
@admin_required
@session_bp.route('/<session_id>', methods=['DELETE'])  
def delete_session(session_id):
    """
    Supprime une session
    """
    session = storage.get(Session, session_id)
    if not session:
        abort(404, description="Session not found")
    
    storage.delete(session)
    storage.save()
    
    return jsonify({"message": "Session deleted"}), 200 
