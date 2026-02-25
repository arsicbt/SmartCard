from flask import Flask, render_template, redirect, url_for, session, request
from functools import wraps
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# URL de l'API backend
API_URL = 'http://localhost:5000/api'


# **********************************************
# Fonctions pour les appels API
# **********************************************
def make_api_request(endpoint, method='GET', data=None, token=None):
    """Helper pour faire des requêtes à l'API backend"""
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    url = f'{API_URL}{endpoint}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return False, {'error': 'Invalid HTTP method'}, 400

        if response.status_code in [200, 201]:
            return True, response.json(), response.status_code
        else:
            return False, response.json(), response.status_code

    except requests.exceptions.ConnectionError:
        return False, {'error': 'Backend API non accessible'}, 500
    except Exception as e:
        return False, {'error': str(e)}, 500


# **********************************************
# Décorateur pour vérifier l'authentification
# **********************************************
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# **********************************************
# Routes Frontend
# **********************************************
@app.route('/')
def index():
    """Page d'accueil - redirige vers dashboard si connecté"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Page de connexion"""
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal avec statistiques réelles depuis l'API"""
    user = session.get('user')
    token = session.get('token')
    user_id = user.get('id')
    user_name = user.get('first_name', 'Utilisateur')

    success, sessions, _ = make_api_request(f'/sessions/user/{user_id}', token=token)
    if not success:
        sessions = []

    total_sessions   = len(sessions)
    quiz_count       = sum(1 for s in sessions if s.get('type') == 'quiz')
    flashcard_count  = sum(1 for s in sessions if s.get('type') == 'flashcard')
    total_correct    = 0
    total_questions  = 0

    for s in sessions:
        if s.get('score') is not None and s.get('max_score') is not None:
            total_correct   += s.get('score', 0)
            total_questions += s.get('max_score', 0)

    accuracy       = int((total_correct / total_questions * 100)) if total_questions > 0 else 0
    cards_progress = min(75, flashcard_count * 5)
    quiz_progress  = min(100, quiz_count * 10)

    stats = {
        'cards_generated': flashcard_count,
        'cards_progress':  cards_progress,
        'quizzes_created': quiz_count,
        'quiz_progress':   quiz_progress,
        'correct_answers': total_correct,
        'accuracy':        accuracy,
        'cards_mastered':  flashcard_count,
        'study_time':      f"{total_sessions * 5}h",
        'streak':          7  # TODO: calculer depuis les dates
    }
    
    success, sessions, status = make_api_request(f'/sessions/user/{user_id}', token=token)

    print("SUCCESS:", success)
    print("STATUS:", status)
    print("SESSIONS:", sessions)

    return render_template('dashboard.html',
                           user_name=user_name,
                           stats=stats,
                           active_view='dashboard')


# **********************************************
# Route - Galerie des Quizz
# **********************************************
@app.route('/quizzes')
@login_required
def quizzes_page():
    """Liste de tous les quiz de l'utilisateur"""
    user  = session.get('user')
    token = session.get('token')
    user_id = user.get('id')

    success, sessions, _ = make_api_request(f'/sessions/user/{user_id}', token=token)
    if not success:
        sessions = []

    # Garder uniquement les QUIZ et enrichir avec le nom du thème
    quizzes = []
    for s in sessions:
        if s.get('type') != 'QUIZ':
            continue

        # Récupérer le nom du thème si disponible
        theme_name = None
        if s.get('theme_id'):
            ok, theme, _ = make_api_request(f'/themes/{s["theme_id"]}', token=token)
            if ok:
                theme_name = theme.get('name')

        quizzes.append({
            'id':              s.get('id'),
            'theme_name':      theme_name or 'Sans thème',
            'questions_count': s.get('questions_count', 0),
            'score':           s.get('score'),
            'max_score':       s.get('max_score'),
            'created_at':      s.get('created_at'),
        })

    # Plus récent en premier
    quizzes.sort(key=lambda x: x['created_at'] or '', reverse=True)

    return render_template('quizzes.html', quizzes=quizzes, active_view='quiz')


# **********************************************
# Route - Création d'une session d'apprentissage
# **********************************************
@app.route('/session')
@login_required
def session_page():
    """Page de création d'une session d'apprentissage"""
    user = session.get('user')
    return render_template('session.html', user_id=user.get('id'))


@app.route('/api/sessions/create-with-pdf', methods=['POST'])
@login_required
def proxy_create_session_with_pdf():
    """Proxy multipart vers l'API backend (le front ne peut pas rediriger un upload fichier)"""
    token = session.get('token')
    user  = session.get('user')

    print(f"[DEBUG] token = {token}")
    print(f"[DEBUG] user  = {user}")

    try:
        pdf_file     = request.files.get('pdf_file')
        session_type = request.form.get('session_type')

        files   = {'pdf_file': (pdf_file.filename, pdf_file.stream, pdf_file.mimetype)}
        data    = {'session_type': session_type, 'user_id': user.get('id')}
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.post(
            f'{API_URL}/sessions/create-with-pdf',
            files=files,
            data=data,
            headers=headers
        )

        return response.json(), response.status_code

    except Exception as e:
        return {'error': str(e)}, 500


# **********************************************
# Route - Flashcards
# **********************************************
@app.route('/cards/<session_id>')
@login_required
def cards_page(session_id):
    """Page de flashcards pour une session donnée"""
    token = session.get('token')

    # Récupérer la session
    success, session_data, _ = make_api_request(f'/sessions/{session_id}', token=token)
    if not success:
        return redirect(url_for('session_page'))

    # Récupérer les questions avec leurs réponses
    cards_data = []
    for q_id in session_data.get('questions_ids', []):
        ok, question, _ = make_api_request(f'/questions/{q_id}', token=token)
        if ok:
            ok_ans, answers, _ = make_api_request(f'/answers/question/{q_id}', token=token)
            question['answer_text'] = answers[0]['answer_text'] if ok_ans and answers else '—'
            cards_data.append(question)

    return render_template('cards.html',
                           session_data=session_data,
                           cards_data=cards_data)


# **********************************************
# Route - Quiz
# **********************************************
@app.route('/quiz/<session_id>')
@login_required
def quiz_page(session_id):
    """Page de quiz pour une session donnée"""
    token = session.get('token')

    # Récupérer la session
    success, session_data, _ = make_api_request(f'/sessions/{session_id}', token=token)
    if not success:
        return redirect(url_for('session_page'))

    # Récupérer les questions avec leurs réponses (choix multiples)
    quiz_data = []
    for q_id in session_data.get('questions_ids', []):
        ok, question, _ = make_api_request(f'/questions/{q_id}', token=token)
        if ok:
            ok_ans, answers, _ = make_api_request(f'/answers/question/{q_id}', token=token)
            question['answers'] = answers if ok_ans else []
            quiz_data.append(question)

    return render_template('quizz.html',
                           session_data=session_data,
                           quiz_data=quiz_data)


# **********************************************
# Routes d'authentification (proxy vers API)
# **********************************************
@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Proxy vers l'API de login"""
    try:
        response = requests.post(
            f'{API_URL}/auth/login',
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()

        if response.status_code == 200:
            session['user']  = data.get('user')
            session['token'] = data.get('token')

        return data, response.status_code

    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Déconnexion"""
    session.clear()
    return {'message': 'Logged out'}, 200


# **********************************************
# Lancement de l'application
# **********************************************
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)