from flask import Blueprint, jsonify, request, abort
from Persistence.DBStorage import storage
from Models.answerModel import Answer
from Utils.authVerification import auth_required, admin_required
from Models.questionModel import Question


answer_bp = Blueprint("answers", __name__, url_prefix="/api/answers")


# ************************************************
# GET ANSWER BY ID
# ************************************************
@admin_required
@answer_bp.route("/<answer_id>", methods=["GET"])
def get_answer(answer_id):
    """Récupère une réponse par ID"""
    answer = storage.get(Answer, answer_id)
    
    if not answer:
        abort(404, description="Answer not found")
        
    return jsonify(answer.to_dict()), 200


# ************************************************
# GET ALL ANSWERS FOR A QUESTION 
# ************************************************
@admin_required
@answer_bp.route("/question/<question_id>", methods=["GET"])
def get_question_answers(question_id):
    """Récupère les réponses d'une question"""
    question = storage.get("Question", question_id)
    if not question:
        abort(404, description="Question not found")
    
    answers = storage.filter_by(Answer, question_id=question_id)
    return jsonify([a.to_dict() for a in answers]), 200


# ************************************************
# CREATE ANSWER
# ************************************************
@auth_required
@answer_bp.route("/", methods=["POST"])
def create_answer():
    """Crée une nouvelle réponse"""
    
    if not request.is_json:
        abort(400, description="Not a JSON")
    
    data = request.get_json()
    
    required_fields = ['answer_text', 'question_id']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")
    

    # Vérifier que la question existe
    question = storage.get(Question, data['question_id'])
    if not question:
        abort(404, description="Question not found")
    
    answer = Answer(
        answer_text=data["answer_text"],
        is_correct=data.get("is_correct", False),
        question_id=data["question_id"]
    )

    storage.new(answer)
    storage.save()

    return jsonify(answer.to_dict()), 201


# ************************************************
# DELETE ASNWER
# ************************************************
@admin_required
@answer_bp.route("/<answer_id>", methods=["DELETE"])
def delete_answer(answer_id):
    """Supprime une réponse"""
    
    answer = storage.get(Answer, answer_id)
    if not answer:
        abort(404, description="Answer not found")
    
    storage.delete(answer)
    storage.save()
    
    return jsonify({}), 200
