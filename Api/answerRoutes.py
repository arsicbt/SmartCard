from flask import jsonify, request, abort
from API.v1.views import app_views
from Persistence.db_storage import storage
from Models.answer import Answer


answer_bp = Blueprint("users", __name__, url_prefix="/answer")


# ************************************************
# GET ANSWER BY ID
# ************************************************\\wsl.localhost\Ubuntu\home\arsi\SmartCard\venv
@app_views.route('/answers/<answer_id>', methods=['GET'], strict_slashes=False)
def get_answer(answer_id):
    """Récupère une réponse par ID"""
    answer = storage.get("Answer", answer_id)
    
    if not answer:
        abort(404)
    
    return jsonify(answer.to_dict())



# ************************************************
# GET ALL ANSWERS
# ************************************************
@app_views.route('/questions/<question_id>/answers', methods=['GET'], strict_slashes=False)
def get_question_answers(question_id):
    """Récupère les réponses d'une question"""
    question = storage.get("Question", question_id)
    if not question:
        abort(404)
    
    answers = storage.filter_by("Answer", question_id=question_id)
    return jsonify([a.to_dict() for a in answers])



# ************************************************
# POST
# ************************************************
@app_views.route('/answers', methods=['POST'], strict_slashes=False)
def create_answer():
    """Crée une nouvelle réponse"""
    
    if not request.json:
        abort(400, description="Not a JSON")
    
    required_fields = ['answer_text', 'question_id']
    for field in required_fields:
        if field not in request.json:
            abort(400, description=f"Missing {field}")
    
    data = request.json
    
    # Vérifier que la question existe
    question = storage.get("Question", data['question_id'])
    if not question:
        abort(404, description="Question not found")
    
    try:
        answer = Answer(
            answer_text=data['answer_text'],
            question_id=data['question_id'],
            is_correct=data.get('is_correct', False)
        )
        
        storage.new(answer)
        storage.save()
        
        # Mettre à jour la question avec l'ID de la réponse
        question.add_answer_id(answer.id)
        storage.save()
        
        return jsonify(answer.to_dict()), 201
        
    except Exception as e:
        abort(400, description=str(e))



# ************************************************
# DELETE
# ************************************************
@app_views.route('/answers/<answer_id>', methods=['DELETE'], strict_slashes=False)
def delete_answer(answer_id):
    """Supprime une réponse"""
    
    answer = storage.get("Answer", answer_id)
    if not answer:
        abort(404)
    
    storage.delete(answer)
    storage.save()
    
    return jsonify({}), 200
