from flask import Blueprint, jsonify, request, abort
from Persistence.DBStorage import storage
from Models.questionModel import Question
from Utils.authVerification import auth_required, admin_required
from Models.tablesSchema import QuestionType, Difficulty
from Models.themeModel import Theme


question_bp = Blueprint("questions", __name__, url_prefix="/api/questions")


# ************************************************
# # GET ALL QUESTIONS
# ************************************************
@admin_required
@question_bp.route("/", methods=["GET"])
def get_questions():
    """
    Récupère toutes les questions
    """
    questions = storage.all(Question)
    return jsonify([q.to_dict() for q in questions.values()]), 200


# ************************************************
# GET QUESTION BY ID
# ************************************************
@admin_required
@question_bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
    """Récupère une question par ID"""
    question = storage.get(Question, question_id)
    
    if not question:
        abort(404, description="Question not found")
    
    return jsonify(question.to_dict()), 200


# ************************************************
# CREATE QUESTION
# ************************************************
@auth_required
@question_bp.route("/", methods=["POST"])
def create_question():
    if not request.is_json:
        abort(400, description="Not a JSON")
    
    data = request.get_json()
    
    required = ["question_text", "theme_id"]
    for field in required:
        if field not in data:
            abort(400, description=f"Missing {field}")
            
    theme = storage.get(Theme, data["theme_id"])

    question = Question(
        question_text=data["question_text"],
        theme_id=data["theme_id"],
        type=QuestionType[data.get('type', 'QUIZ').upper()],
        difficulty=Difficulty[data.get('difficulty', 'MEDIUM').upper()],
        explanation=data.get("explanation")
    )

    storage.new(question)
    storage.save()

    return jsonify(question.to_dict()), 201


# ************************************************
# UPDATE QUESTION
# ************************************************
@auth_required
@question_bp.route("/<question_id>", methods=["PUT"])
def update_question(question_id):
    """Met à jour une question"""
    
    question = storage.get(Question, question_id)
    if not question:
        abort(404)
    
    if not request.is_json:
        abort(400, description="Not a JSON")
    
    ignore = ["id", "theme_id", "created_at", "updated_at", "deleted_at"]

    for key, value in request.json.items():
        if key not in ignore and hasattr(question, key):
            setattr(question, key, value)

    return jsonify(question.to_dict()), 200


# ************************************************
# DELETE QUESTION
# ************************************************
@admin_required
@question_bp.route("/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    """Supprime une question"""
    
    question = storage.get(Question, question_id)
    if not question:
        abort(404)
    
    storage.delete(question)
    storage.save()
    
    return jsonify({"message": "Question deleted"}), 200
