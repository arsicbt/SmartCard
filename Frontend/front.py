from flask import Flask, render_template, redirect, url_for, session, request
from functools import wraps
import requests
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# URL de l'API backend
API_URL = 'http://localhost:5000/api'


# **********************************************
# Fonctions pour les appels API
# **********************************************
from werkzeug.exceptions import Unauthorized

def make_api_request(endpoint, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    url = f'{API_URL}{endpoint}'

    try:
        response = requests.request(method, url, json=data, headers=headers)
        
        if response.status_code == 401:
            refresh_token = session.get('refresh_token')
            
            if refresh_token:
                refresh_response = requests.post(
                    f'{API_URL}/auth/refresh',
                    json={'refresh_token': refresh_token}
                )
                
                if refresh_response.status_code == 200:
                    new_token = refresh_response.json().get('access_token')
                    session['token'] = new_token
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.request(method, url, json=data, headers=headers)
                else:
                    session.clear()
                    raise Unauthorized()
            else:
                session.clear()
                raise Unauthorized()

        if response.status_code in [200, 201]:
            return True, response.json(), response.status_code
        else:
            return False, response.json(), response.status_code

    except Unauthorized:
        raise
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
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # 1. Récupérer l'utilisateur et le token
    user = session.get('user')
    token = session.get('token')
    user_id = user.get('id')
    user_name = user.get('first_name', 'Utilisateur')

    # 2. Récupérer les sessions depuis l'API
    success, sessions, _ = make_api_request(f'/sessions/user/{user_id}', token=token)
    if not success:
        sessions = []

    # 3. Calculer les statistiques de base
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

    # 4. Calculer les données du graphique (7 derniers jours)
    today = datetime.now()
    chart_data = {
        'labels': [],
        'cards_created': [],
        'study_time': []
    }
    
    sessions_by_day = defaultdict(lambda: {'cards': 0, 'time': 0})
    
    for i in range(6, -1, -1):  # 7 jours en arrière
        day = today - timedelta(days=i)
        day_name = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][day.weekday()]
        day_key = day.strftime('%Y-%m-%d')
        chart_data['labels'].append(day_name)
        
        # Compter les sessions créées ce jour
        for s in sessions:
            created_at = s.get('created_at', '')
            if created_at and created_at.startswith(day_key):
                sessions_by_day[day_key]['cards'] += 1
                sessions_by_day[day_key]['time'] += 5  # 5 min par session
        
        chart_data['cards_created'].append(sessions_by_day[day_key]['cards'])
        chart_data['study_time'].append(sessions_by_day[day_key]['time'])

    # 5. Préparer les stats pour le template
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

    # 6. Rendre le template
    return render_template('dashboard.html',
                           user_name=user_name,
                           stats=stats,
                           chart_data=chart_data,
                           active_view='dashboard')

# **********************************************
# Route - Galerie des Quizz
# **********************************************
@app.route('/quizzes-list')
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
        if s.get('type') != 'quiz':
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


@app.route('/cards-list')
@login_required
def card_list():
    """Page listant toutes les sessions flashcard de l'utilisateur"""
    from datetime import datetime, timedelta
    
    user = session.get('user')
    token = session.get('token')
    user_id = user.get('id')
    
    # Récupérer toutes les sessions de l'utilisateur
    success, sessions, _ = make_api_request(f'/sessions/user/{user_id}', token=token)
    
    if not success:
        sessions = []
    
    # Filtrer uniquement les sessions FLASHCARD
    cards = []
    for s in sessions:
        if s.get('type', '').upper() == 'FLASHCARD':
            # Enrichir avec le nom du thème si possible
            theme_id = s.get('theme_id')
            theme_name = 'Sans thème'
            
            if theme_id:
                # Optionnel : récupérer le nom du thème depuis l'API
                # success_theme, theme_data, _ = make_api_request(f'/themes/{theme_id}', token=token)
                # if success_theme:
                #     theme_name = theme_data.get('name', 'Sans thème')
                pass
            
            cards.append({
                'id': s.get('id'),
                'theme_name': theme_name,
                'questions_count': s.get('questions_count', 0),
                'started_at': s.get('started_at'),
                'completed_at': s.get('completed_at'),
                'created_at': s.get('created_at')
            })
    
    # Trier par date de création (plus récent en premier)
    cards.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('cards-list.html', 
                         cards=cards,
                         active_view='cards')


# **********************************************
# Route - Création d'une session d'apprentissage
# **********************************************
@app.route('/session')
@login_required
def session_page():
    """Page de création d'une session d'apprentissage"""

    user = session.get('user')
    token = session.get('token')
    user_id = user.get('id')
    
    success, sessions, _ = make_api_request(f'/sessions/user/{user_id}', token=token)
    if not success:
        sessions = []

    if sessions:
        print("DEBUG SESSION:", sessions[0])
    
    return render_template('session.html', user_id=user_id)

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


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
@login_required
def proxy_delete_session(session_id):
    """Proxy pour supprimer une session"""
    token = session.get('token')
    
    try:
        response = requests.delete(
            f'http://localhost:5000/api/sessions/{session_id}',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            return response.json(), response.status_code
    
    except Exception as e:
        return {'error': str(e)}, 500


# **********************************************
# Routes d'authentification (proxy vers API)
# **********************************************
@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Proxy vers l'API de login"""
    try:
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=request.json
        )
        
        data = response.json()
        
        if response.status_code == 200:
            session['user'] = data.get('user')
            session['token'] = data.get('token') 
            session['refresh_token'] = data.get('refresh_token') 
        
        return data, response.status_code
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/logout')
def logout():
    """Déconnexion - nettoie la session et redirige vers login"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Déconnexion via API (pour AJAX)"""
    session.clear()
    return {'message': 'Logged out'}, 200

from datetime import datetime

@app.context_processor
def inject_current_year():
    """Injecte l'année courante dans tous les templates"""
    return {'current_year': datetime.now().year}

# **********************************************
# Lancement de l'application
# **********************************************
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)