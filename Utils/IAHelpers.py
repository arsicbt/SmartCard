
from flask import Blueprint, request, jsonify, abort
import os
import PyPDF2
import json
import requests

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"pdf"}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ****************************************************************************
# HELPERS IA
# ****************************************************************************

def extract_text_from_pdf(file_path: str) -> str:
    """Extrait texte d'un PDF"""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Erreur extraction PDF: {str(e)}")


def analyze_theme(text: str) -> dict:
    """Analyse thème via GROQ"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY manquante")
    
    text_sample = text[:8000] if len(text) > 8000 else text
    
    prompt = f"""Analyse ce texte et retourne UNIQUEMENT un JSON:

{{
  "name": "Nom du thème en français (max 100 caractères)",
  "keywords": ["mot-clé1", "mot-clé2", "mot-clé3"],
  "description": "Description en 1-2 phrases"
}}

TEXTE:
{text_sample}"""
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        },
        timeout=30
    )
    
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    return json.loads(content)


def generate_questions(text: str, session_type: str, difficulty: str, count: int) -> list:
    """Génère questions via GROQ"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY manquante")
    
    text_sample = text[:6000] if len(text) > 6000 else text
    count = min(count, 20)
    
    if session_type == "quiz":
        prompt = f"""Génère {count} QCM depuis ce texte. JSON uniquement:

{{
  "questions": [
    {{
      "question_text": "Question?",
      "type": "quiz",
      "difficulty": "{difficulty}",
      "explanation": "Explication",
      "answers": [
        {{"answer_text": "Bonne", "is_correct": true}},
        {{"answer_text": "Mauvaise 1", "is_correct": false}},
        {{"answer_text": "Mauvaise 2", "is_correct": false}}
      ]
    }}
  ]
}}

TEXTE: {text_sample}"""
    else:
        prompt = f"""Génère {count} flashcards depuis ce texte. JSON uniquement:

{{
  "questions": [
    {{
      "question_text": "Question (RECTO)?",
      "type": "flashcard",
      "difficulty": "{difficulty}",
      "explanation": "Réponse détaillée (VERSO)",
      "answers": [{{"answer_text": "Réponse courte", "is_correct": true}}]
    }}
  ]
}}

TEXTE: {text_sample}"""
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 3000
        },
        timeout=60
    )
    
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    
    data = json.loads(content)
    return data.get("questions", [])


def process_ai_session(session: Session, text: str):
    """
    Traite une session IA (PDF ou texte)
    
    Workflow:
    1. Analyse thème
    2. Création/matching thème
    3. Génération questions
    4. Sauvegarde questions + réponses
    5. Mise à jour session
    """
    session.mark_as_processing()
    storage.save()
    
    try:
        # 1. Analyse thème
        print("Elon analyse le thème...")
        theme_data = analyze_theme(text)
        print(f"Thème généré ! : {theme_data['name']}")
        
        # 2. Matching/création thème
        existing_themes = storage.filter_by(
            Theme,
            name=theme_data["name"],
            user_id=session.user_id
        )
        
        if existing_themes:
            theme = existing_themes[0]
            print(f"Thème existant: {theme.id}")
        else:
            theme = Theme(
                user_id=session.user_id,
                name=theme_data["name"],
                description=theme_data.get("description", ""),
                keywords=theme_data.get("keywords", [])
            )
            storage.new(theme)
            storage.save()
            print(f"Nouveau thème: {theme.id}")
        
        # Lier session au thème
        session.theme_id = theme.id
        
        # 3. Génération questions
        ai_config = session.ai_config
        difficulty = ai_config.get("difficulty", "medium")
        count = ai_config.get("question_count", 10)
        
        print(f"Elon au charbon: Génération {count} questions ({session.type})...")
        questions_json = generate_questions(text, session.type, difficulty, count)
        print(f"{len(questions_json)} questions générées, va travailler maintenant....")
        
        # 4. Sauvegarde questions + réponses
        question_ids = []
        
        for q_data in questions_json:
            question = Question(
                theme_id=theme.id,
                type=q_data["type"],
                difficulty=q_data.get("difficulty", "medium"),
                question_text=q_data["question_text"],
                explanation=q_data.get("explanation", ""),
                source="ai_generated"
            )
            storage.new(question)
            storage.save()
            
            for i, a_data in enumerate(q_data["answers"]):
                answer = Answer(
                    question_id=question.id,
                    answer_text=a_data["answer_text"],
                    is_correct=a_data.get("is_correct", False),
                    order_position=i
                )
                storage.new(answer)
            
            storage.save()
            question_ids.append(question.id)
        
        # 5. Marquer session comme complétée
        session.mark_as_completed(question_ids)
        
        # 6. Nettoyer fichier temporaire
        session.cleanup_source()
        
        storage.save()
        print("Traitement terminé !!")
        
    except Exception as e:
        print(f"Hoho erreur !! : {str(e)}")
        session.mark_as_failed(str(e))
        storage.save()
        raise
