"""
sessionRoutes.py — Routes HTTP pour les sessions
"""

from flask import Blueprint, jsonify, request, abort
from Models.sessionModel import Session
from Models.tablesSchema import SessionType
from Models.userModel import User
from Models.themeModel import Theme
from Models.questionModel import Question
from Models.answerModel import Answer
from Utils.authVerification import auth_required, admin_required
from Persistence.DBStorage import storage
from Services.pdfAnalysisService import PDFAnalysisService
from Services.similarityService import SimilarityService

session_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


# ************************************************
# GET SESSIONS BY USER ID
# ************************************************
@session_bp.route('/user/<user_id>', methods=['GET'])
@admin_required
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
@session_bp.route('/<session_id>', methods=['GET'])
@admin_required
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
@session_bp.route('/', methods=['POST'])
@auth_required
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
@session_bp.route('/<session_id>', methods=['PUT'])
@auth_required
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
@session_bp.route('/<session_id>', methods=['DELETE'])  
@admin_required
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



# ************************************************
# POST - CREATE SESSION WITH PDF ANALYSIS
# ************************************************
@session_bp.route('/create-with-pdf', methods=['POST'])
@auth_required
def create_session_with_pdf():
    """
    Crée une session en analysant un PDF
    
    Flow:
    1. User choisit le type de session (QUIZ ou FLASHCARD)
    2. Upload du PDF
    3. Analyse automatique du PDF par Groq → extraction du thème
    4. Recherche de thème existant avec ≥40% de correspondance
    5. Si thème trouvé : récupérer questions existantes avec ≥40% de similarité
    6. Si pas assez de questions : générer avec Groq
    7. Transformer les questions selon le type (Quiz/Cards)
    8. Créer la session avec les questions
    
    Params (multipart/form-data):
        - user_id: ID de l'utilisateur
        - session_type: "QUIZ" ou "FLASHCARD"
        - pdf_file: Fichier PDF à analyser
        - questions_count: Nombre de questions (optionnel, défaut 10)
    
    Returns:
        Session créée avec les questions générées
    """
    # Vérifier le user_id
    user_id = request.form.get('user_id')
    if not user_id:
        abort(400, desciption="Missins user_id")
        
    user = storage.get(User, user_id)
    if not user:
        abort(404, description="User not found")
        
    # Vérifier le type de la session
    session_type = request.form.get('session_type', '').upper()
    if session_type not in ["QUIZZ", "FLASHCARD"]:
        abort(400, description="Invalid sessio_type. Must be QUIZZ or FLASHCARD")
        
    # Vérifier le fichier PDF
    if 'pdf_file' not in request.files:
        abort(400, description="Missing pdf_file")
    
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        abort(400, description="No file selected")

    if not pdf_file.filename.lower().endwith('.pdf'):
        abort(400, description="File must be a PDF")
        
    # Nombre de questions
    try:
        question_count = int(request.form.get('questions_count', 10))
        if questions_ocount < 1 or questions_count > 50:
            avort(400, description="question_count must be between 1 and 50")
    except ValueError:
        abort(400, description="Invalid question_count")
        
    try:
        # ********************************************************
        # ÉTAPE 1 : ANALYSER LE PDF
        # ********************************************************
        analysis_result = PDFAnalysisService.analyse_pdf_full_pipeline(
            pdf_file,
            session_type,
            questions_count
        )
        
        pdf_content = analysis_result['pdf_content']
        theme_data = analysis_result['theme']
        generated_questions = analysis_result['questions']
        
        # ********************************************************
        # ÉTAPE 2 : RECHERCHER UN THÈME EXISTANT
        # ********************************************************
        
        # Récupérer tous les thèmes de l'utilisateur
        user_themes = storage.filter_by(Theme, user_id=user_id)
        
        # Cinvertir en dict pour le service de similarité
        themes_dict = [
            {
                'id': t.id,
                'name': t.name,
                'keywords': t.keywords,
                'description': t.description
            }
            for t in user_themes
        ]
        
        # Chercher une thème correspondant (>= 40 %)
        matching_theme = SimilarityService.find_matching_theme(
            theme_data['keywords'],
            themes_dict,
            threshold=0.4
        )
        
        theme_id = None
        theme_name = theme_date['theme_name']
        
        if matching_theme:
            # theme trouvé dans ma DB 
            theme_id = matching_theme['theme']['id']
            theme_name = matching_theme['theme']['name']
            theme = storage.get(Theme, theme_id)
            
            # Incrémenter l'usage du theme
            theme.increment_usage()
            
            # ********************************************************
            # ÉTAPE 3 : RÉCUPÉRER LES QUESTIONS EXISTANTES
            # ********************************************************
            existing_questions = storage.filter_by(Question, theme_id=theme_id)
            
            # Convertir en dictionnaire
            question_dict = [
                {
                    'id': q.id,
                    'question_text': q.question_text,
                    'type': q.type.value,
                    'difficulty': q.difficulty.value
                }
                for q in existing_questions
            ]
            
            # Trouver les question avec minimum 40% de similarité
            matching_questions = SimilarityService.find_matching_questions(
                pdf_content,
                question_dict,
                threshold= 0.4
            )
            
            # Limiter au noombre demandé
            matching_questions = matching_questions[:questions_count]
            
            # Si pas assez de questions dans la DB, compléter avec des générées
            questions_ids = [q['question']['id'] for q in matching_questions]
            
            if len(questions_ids) < questions_count:
                # Créer les questions manquantes grace à Groq
                remaining_count = qustion_count - len(questions_ids)
                new_questions_ids = _create_questions_from_generated(
                    generated_questions[:remaining_count],
                    theme_id,
                    session_type 
                )
                question_ids.extend(new_question_ids)
                
        else:
            # ********************************************************
            # ÉTAPE 4 : CRÉER UN NOUVEAU THÈME
            # ********************************************************
            new_theme = Theme(
                user_id=user_id,
                name=theme_data['theme_name'],
                description=theme_data['description'],
                keyword=theme_data['keywords'],
                question_count=0
            )
            
            storage.new(new_theme)
            storage.save()
            
            theme_id = new_theme.identifier
            
            # Créer toutes les questions depuis Groq
            quetion_ids = _create_questions_from_generated(
                generated_questions,
                theme_id,
                session_type
            )
            
            # Mettre à jor le compteur 
            new_theme.questions_count = len(questions_ids)
                
        # ********************************************************
        # ÉTAPE 5 : CRÉER LA SESSION
        # ********************************************************
        session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=session_type,
            questions_ids=question_ids,
            questions_count=len(question_ids)
        )  
            
        storage.new(session)
        storage.save()
        
        # ********************************************************
        # RETOUR
        # ********************************************************
        return jsonify({
            "session": session.to_dict(),
            "theme": {
                "id": theme_id,
                "name": theme_name,
                "was_existing": matching_theme is not None
            },
            "questions_count": len(question_ids),
            "pdf_analysed": True
        }), 201
            
    except ValueError as e:
        sotrage.rollback()
        abort(400, description=str(e))
        
    except Execption as e:
        storage.rollback()
        abort(500, description=f"Error creating session: {str(e)}")
        
        
def _create_questions_from_generated(
    generated_questions_from_generated: list,
    theme_id: str,
    sesion_type: str
) -> list:
    """
    Crée des objets Question et Answer depuis les questions générées par Groq
    
    Args:
        generated_questions: Questions générées par Groq
        theme_id: ID du thème
        session_type: QUIZ ou FLASHCARD
    
    Returns:
        Liste des IDs des questions créées
    """
    from Models.tablesSchema import QuestionType, Difficulty
    
    question_ids = []
    
    for q_data in generated_questions:
        # Créer la question
        question = Question(
            theme_id=theme_id,
            type=QuestionType[sessionn_type],
            question_text=q_data['question'],
            difficulty=Difficulty[q_data.get('difficulty', 'MEDIUM')],
        )
        
        storage.new(question)
        storage.save()
        
        if session_type == 'QUIZZ':
            # QUIZZ: 4 réponses
            for idx, ans_data in enumerate(q_data['anwers']):
                answer = Answer(
                    question_id=question.id,
                    answer_text=ans_data['text'],
                    is_correct=ans_data['is_correct'],
                    order_position=idx 
                )
                storage.new(answer)
        else:
            # FLASHCARD: 1 réponse
            answer = Answer(
                question_id=question.id,
                answer_text=q_data['answer'],
                is_correct=True,
                order_position=0
            )
            storage.new(answer)

        storage.save()
        question_ids.append(question.id)
        
    return question_ids
