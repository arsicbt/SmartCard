"""
sessionRoutes.py — Routes HTTP pour les sessions
"""

from flask import Blueprint, jsonify, request, abort
from Models.sessionModel import Session
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
@auth_required 
def delete_session(session_id):
    """
    Supprime une session
    """
    session_obj = storage.get(Session, session_id)
    if not session_obj:
        abort(404, description="Session not found")
    
    current_user = request.current_user
    
    if session_obj.user_id != current_user.id and not current_user.is_admin:
        abort(403, description="Vous n'êtes pas autorisé à supprimer cette session")
        
    storage.delete(session_obj)
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
    """
    
    print("\n" + "="*80)
    print("[DEBUG] === CREATE SESSION WITH PDF - START ===")
    print("="*80)
    
    try:
        # ********************************************************
        # VALIDATION DES PARAMÈTRES
        # ********************************************************
        print("\n[DEBUG] 1. VALIDATION DES PARAMÈTRES")
        
        # Vérifier le user_id
        user_id = request.form.get('user_id')
        print(f"[DEBUG]   - user_id: {user_id}")
        
        if not user_id:
            print("[ERROR]   ❌ user_id manquant!")
            abort(400, description="Missing user_id")
            
        user = storage.get(User, user_id)
        print(f"[DEBUG]   - User trouvé: {user is not None}")
        
        if not user:
            print("[ERROR]   ❌ User non trouvé!")
            abort(404, description="User not found")
            
        # Vérifier le type de la session
        session_type = request.form.get('session_type', '').upper()
        print(f"[DEBUG]   - session_type: {session_type}")
        
        if session_type not in ["QUIZ", "FLASHCARD"]:
            print(f"[ERROR]   ❌ Type invalide: {session_type}")
            abort(400, description="Invalid session_type. Must be QUIZ or FLASHCARD")
            
        # Vérifier le fichier PDF
        print(f"[DEBUG]   - Files reçus: {list(request.files.keys())}")
        
        if 'pdf_file' not in request.files:
            print("[ERROR]   ❌ pdf_file manquant!")
            abort(400, description="Missing pdf_file")
        
        pdf_file = request.files['pdf_file']
        print(f"[DEBUG]   - Filename: {pdf_file.filename}")
        
        if pdf_file.filename == '':
            print("[ERROR]   ❌ Nom fichier vide!")
            abort(400, description="No file selected")

        if not pdf_file.filename.lower().endswith('.pdf'):
            print(f"[ERROR]   ❌ Pas un PDF: {pdf_file.filename}")
            abort(400, description="File must be a PDF")
           
        # Nombre de questions
        try:
            questions_count = int(request.form.get('questions_count', 10))
            print(f"[DEBUG]   - questions_count: {questions_count}")
            
            if questions_count < 1 or questions_count > 50:
                print(f"[ERROR]   ❌ questions_count hors limites: {questions_count}")
                abort(400, description="questions_count must be between 1 and 50")
        except ValueError as e:
            print(f"[ERROR]   ❌ questions_count invalide: {e}")
            abort(400, description="Invalid questions_count")
            
        print("[DEBUG]   ✅ Validation OK\n")
        
        # ********************************************************
        # ÉTAPE 1 : ANALYSER LE PDF
        # ********************************************************
        print("[DEBUG] 2. ANALYSE DU PDF")
        print("[DEBUG]   - Appel PDFAnalysisService.analysis_pdf_full_pipeline...")
        
        analysis_result = PDFAnalysisService.analysis_pdf_full_pipeline(
            pdf_file,
            session_type,
            questions_count
        )
        
        print(f"[DEBUG]   - Résultat analyse: {type(analysis_result)}")
        print(f"[DEBUG]   - Keys: {analysis_result.keys() if isinstance(analysis_result, dict) else 'Not a dict'}")
        
        # Vérifier structure retour
        if not isinstance(analysis_result, dict):
            print(f"[ERROR]   ❌ analysis_result n'est pas un dict: {type(analysis_result)}")
            abort(500, description="Invalid analysis result format")
            
        # Extraire les données
        theme_data = analysis_result.get('theme_data')
        generated_questions = analysis_result.get('generated_questions')
        pdf_content = analysis_result.get('pdf_content', '')
        
        print(f"[DEBUG]   - theme_data: {theme_data is not None}")
        print(f"[DEBUG]   - generated_questions: {len(generated_questions) if generated_questions else 0} questions")
        print(f"[DEBUG]   - pdf_content length: {len(pdf_content)} caractères")
        
        if not theme_data or not generated_questions:
            print("[ERROR]   ❌ Données manquantes dans analysis_result!")
            abort(500, description="Incomplete analysis result")
            
        print("[DEBUG]   ✅ Analyse PDF OK\n")
        
        # ********************************************************
        # ÉTAPE 2 : RECHERCHER UN THÈME EXISTANT
        # ********************************************************
        print("[DEBUG] 3. RECHERCHE THÈME EXISTANT")
        
        # Récupérer tous les thèmes de l'utilisateur
        user_themes = storage.filter_by(Theme, user_id=user_id)
        print(f"[DEBUG]   - Thèmes utilisateur: {len(user_themes)}")
        
        # Convertir en dict pour le service de similarité
        themes_dict = [
            {
                'id': t.id,
                'name': t.name,
                'keywords': t.keywords,
                'description': t.description
            }
            for t in user_themes
        ]
        print(f"[DEBUG]   - themes_dict créé: {len(themes_dict)} thèmes")
        
        # Chercher un thème correspondant (>= 40 %)
        print(f"[DEBUG]   - Recherche similarité avec keywords: {theme_data.get('keywords', [])[:3]}...")
        
        matching_theme = SimilarityService.find_matching_theme(
            theme_data['keywords'],
            themes_dict,
            threshold=0.4
        )
        
        print(f"[DEBUG]   - Matching theme: {matching_theme is not None}")
        
        theme_id = None
        theme_name = theme_data['theme_name']
        
        if matching_theme:
            print("[DEBUG]   ✅ Thème existant trouvé!")
            
            # Thème trouvé dans la DB 
            theme_id = matching_theme['theme']['id']
            theme_name = matching_theme['theme']['name']
            similarity = matching_theme['match_score']
            
            print(f"[DEBUG]   - Theme ID: {theme_id}")
            print(f"[DEBUG]   - Theme name: {theme_name}")
            print(f"[DEBUG]   - Similarité: {similarity:.2%}")
            
            theme = storage.get(Theme, theme_id)
            
            # Incrémenter l'usage du thème
            print("[DEBUG]   - Incrémentation usage...")
            theme.increment_usage()
            
            # ********************************************************
            # ÉTAPE 3 : RÉCUPÉRER LES QUESTIONS EXISTANTES
            # ********************************************************
            print("\n[DEBUG] 4. RÉCUPÉRATION QUESTIONS EXISTANTES")
            
            existing_questions = storage.filter_by(Question, theme_id=theme_id)
            print(f"[DEBUG]   - Questions existantes: {len(existing_questions)}")
            
            # Convertir en dictionnaire
            questions_dict = [
                {
                    'id': q.id,
                    'question_text': q.question_text,
                    'type': q.type.value,
                    'difficulty': q.difficulty.value
                }
                for q in existing_questions
            ]
            
            # Trouver les questions avec minimum 40% de similarité
            print("[DEBUG]   - Recherche questions similaires...")
            
            matching_questions = SimilarityService.find_matching_questions(
                pdf_content,
                questions_dict,
                threshold=0.4
            )
            
            print(f"[DEBUG]   - Questions similaires trouvées: {len(matching_questions)}")
            
            # Limiter au nombre demandé
            matching_questions = matching_questions[:questions_count]
            print(f"[DEBUG]   - Questions retenues: {len(matching_questions)}")
            
            # Si pas assez de questions dans la DB, compléter avec des générées
            questions_ids = [q['question']['id'] for q in matching_questions]
            print(f"[DEBUG]   - IDs récupérés: {len(questions_ids)}")
            
            if len(questions_ids) < questions_count:
                print(f"[DEBUG]   ⚠️  Pas assez de questions, génération complément...")
                
                # Créer les questions manquantes grâce à Groq
                remaining_count = questions_count - len(questions_ids)
                print(f"[DEBUG]   - Questions à créer: {remaining_count}")
                
                new_question_ids = _create_questions_from_generated(
                    generated_questions[:remaining_count],
                    theme_id,
                    session_type 
                )
                
                print(f"[DEBUG]   - Nouvelles questions créées: {len(new_question_ids)}")
                questions_ids.extend(new_question_ids)
                
        else:
            print("[DEBUG]   ⚠️  Aucun thème similaire trouvé")
            
            # ********************************************************
            # ÉTAPE 4 : CRÉER UN NOUVEAU THÈME
            # ********************************************************
            print("\n[DEBUG] 4. CRÉATION NOUVEAU THÈME")
            print(f"[DEBUG]   - Name: {theme_data['theme_name']}")
            print(f"[DEBUG]   - Keywords: {theme_data['keywords'][:3] if theme_data['keywords'] else []}")
            
            new_theme = Theme(
                user_id=user_id,
                name=theme_data['theme_name'],
                description=theme_data.get('description', ''),
                keywords=theme_data.get('keywords', []),
                questions_count=0
            )
            
            storage.new(new_theme)
            storage.save()
            
            theme_id = new_theme.id
            print(f"[DEBUG]   - Thème créé avec ID: {theme_id}")
            
            # Créer toutes les questions depuis Groq
            print(f"[DEBUG]   - Création {len(generated_questions)} questions depuis Groq...")
            
            questions_ids = _create_questions_from_generated(
                generated_questions,
                theme_id,
                session_type
            )
            
            print(f"[DEBUG]   - Questions créées: {len(questions_ids)}")
            
            # Mettre à jour le compteur 
            new_theme.questions_count = len(questions_ids)
            storage.save()
            
        print(f"[DEBUG]   ✅ Total questions pour session: {len(questions_ids)}\n")
                
        # ********************************************************
        # ÉTAPE 5 : CRÉER LA SESSION
        # ********************************************************
        print("[DEBUG] 5. CRÉATION SESSION")
        print(f"[DEBUG]   - user_id: {user_id}")
        print(f"[DEBUG]   - theme_id: {theme_id}")
        print(f"[DEBUG]   - type: {session_type}")
        print(f"[DEBUG]   - questions_count: {len(questions_ids)}")
        
        session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=session_type,
            questions_ids=questions_ids, 
            questions_count=len(questions_ids)
        )  
            
        storage.new(session)
        storage.save()
        
        print(f"[DEBUG]   - Session créée avec ID: {session.id}")
        print("[DEBUG]   ✅ Session sauvegardée\n")
        
        # ********************************************************
        # RETOUR
        # ********************************************************
        print("[DEBUG] 6. RETOUR RÉPONSE")
        
        response_data = {
            "session": session.to_dict(),
            "theme": {
                "id": theme_id,
                "name": theme_name,
                "was_existing": matching_theme is not None
            },
            "questions_count": len(questions_ids),
            "pdf_analysed": True
        }
        
        print(f"[DEBUG]   - Response keys: {response_data.keys()}")
        print("\n" + "="*80)
        print("[DEBUG] === CREATE SESSION WITH PDF - SUCCESS ===")
        print("="*80 + "\n")
        
        return jsonify(response_data), 201
            
    except ValueError as e:
        print("\n" + "="*80)
        print(f"[ERROR] ❌ ValueError attrapée!")
        print(f"[ERROR] Type: {type(e).__name__}")
        print(f"[ERROR] Message: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        abort(400, description=str(e))
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"[ERROR] ❌ Exception générale attrapée!")
        print(f"[ERROR] Type: {type(e).__name__}")
        print(f"[ERROR] Message: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        storage.rollback()
        abort(500, description=f"Error creating session: {str(e)}")
        
        
def _create_questions_from_generated(
    generated_questions: list,
    theme_id: str,
    session_type: str
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
    
    print(f"\n[DEBUG] _create_questions_from_generated:")
    print(f"[DEBUG]   - Nombre questions: {len(generated_questions)}")
    print(f"[DEBUG]   - theme_id: {theme_id}")
    print(f"[DEBUG]   - session_type: {session_type}")
    
    question_ids = []
    
    for idx, q_data in enumerate(generated_questions):
        print(f"\n[DEBUG]   Question {idx+1}/{len(generated_questions)}:")
        print(f"[DEBUG]     - Texte: {q_data.get('question', '')[:50]}...")
        
        try:
            # Créer la question
            question = Question(
                theme_id=theme_id,
                type=QuestionType[session_type],
                question_text=q_data['question'],
                difficulty=Difficulty[q_data.get('difficulty', 'MEDIUM').upper()],
            )
            
            storage.new(question)
            storage.save()
            
            print(f"[DEBUG]     - Question créée ID: {question.id}")
            
            if session_type == 'QUIZ':
                # QUIZ: 4 réponses
                print(f"[DEBUG]     - Création {len(q_data.get('answers', []))} réponses QUIZ")
                
                for ans_idx, ans_data in enumerate(q_data['answers']):
                    answer = Answer(
                        question_id=question.id,
                        answer_text=ans_data['text'],
                        is_correct=ans_data['is_correct'],
                        order_position=ans_idx 
                    )
                    storage.new(answer)
                    print(f"[DEBUG]       - Réponse {ans_idx+1}: {ans_data['text'][:30]}... (correct={ans_data['is_correct']})")
            else:
                # FLASHCARD: 1 réponse
                print(f"[DEBUG]     - Création 1 réponse FLASHCARD")
                
                answer = Answer(
                    question_id=question.id,
                    answer_text=q_data['answer'],
                    is_correct=True,
                    order_position=0
                )
                storage.new(answer)
                print(f"[DEBUG]       - Réponse: {q_data['answer'][:30]}...")

            storage.save()
            question_ids.append(question.id)
            
            print(f"[DEBUG]     ✅ Question {idx+1} sauvegardée")
            
        except Exception as e:
            print(f"[ERROR]     ❌ Erreur création question {idx+1}:")
            print(f"[ERROR]     {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
    print(f"\n[DEBUG]   ✅ Total questions créées: {len(question_ids)}")
    return question_ids