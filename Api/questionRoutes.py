from flask import jsonify, request, abort
from Persistence.db_storage import storage
from Models.question import Question



# ************************************************
# GET BY QUESTION BY ID
# ************************************************
@app_views.route('/questions', methods=['GET'], strict_slashes=False)
def get_questions():
    """
    Récupère toutes les questions
    """
    questions = storage.all("Question")
    return jsonify([q.to_dict() for q in questions.values()])


# ************************************************
# GET ALL QUESTIONS
# ************************************************
@app_views.route('/questions/<question_id>', methods=['GET'], strict_slashes=False)
def get_question(question_id):
    """Récupère une question par ID"""
    question = storage.get("Question", question_id)
    
    if not question:
        abort(404)
    
    return jsonify(question.to_dict())


# ************************************************
# GET QUESTION BY THEME ID
# ************************************************
@app_views.route('/themes/<theme_id>/questions', methods=['GET'], strict_slashes=False)
def get_theme_questions(theme_id):
    """Récupère les questions d'un thème"""
    theme = storage.get("Theme", theme_id)
    if not theme:
        abort(404)
    
    questions = storage.filter_by("Question", theme_id=theme_id)
    return jsonify([q.to_dict() for q in questions])



# ************************************************
# POST
# ************************************************
@app_views.route('/questions', methods=['POST'], strict_slashes=False)
def create_question():
    """Crée une nouvelle question"""
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    required_fields = ['question_text', 'theme_id']
    for field in required_fields:
        if field not in request.json:
            abort(400, description=f"Missing {field}")
    
    data = request.json
    
    # Vérifier que le thème existe
    theme = storage.get("Theme", data['theme_id'])
    if not theme:
        abort(404, description="Theme not found")
    
    try:
        question = Question(
            question_text=data['question_text'],
            theme_id=data['theme_id'],
            question_type=data.get('type', 'quiz'),
            difficulty=data.get('difficulty', 'medium'),
            explanation=data.get('explanation')
        )
        
        storage.new(question)
        storage.save()
        
        return jsonify(question.to_dict()), 201
        
    except Exception as e:
        abort(400, description=str(e))



# ************************************************
# PUT
# ************************************************
@app_views.route('/questions/<question_id>', methods=['PUT'], strict_slashes=False)
def update_question(question_id):
    """Met à jour une question"""
    
    question = storage.get("Question", question_id)
    if not question:
        abort(404)
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    data = request.json
    ignore_keys = ['id', 'theme_id', 'created_at', 'updated_at', 'deleted_at']
    
    for key, value in data.items():
        if key not in ignore_keys and hasattr(question, key):
            setattr(question, key, value)
    
    question.update_timestamp()
    storage.save()
    
    return jsonify(question.to_dict())



# ************************************************
# DELETE
# ************************************************
@app_views.route('/questions/<question_id>', methods=['DELETE'], strict_slashes=False)
def delete_question(question_id):
    """Supprime une question"""
    
    question = storage.get("Question", question_id)
    if not question:
        abort(404)
    
    storage.delete(question)
    storage.save()
    
    return jsonify({}), 200
