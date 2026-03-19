from datetime import datetime
from werkzeug.exceptions import Unauthorized
from flask import Flask, render_template, redirect, url_for, session, request, flash
from functools import wraps
import requests
import os
from datetime import datetime, timedelta
from collections import defaultdict
import random

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# URL de l'API backend
API_URL = 'http://localhost:5000/api'


# **********************************************
# Fonctions pour les appels API
# **********************************************


def make_api_request(endpoint, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    url = f'{API_URL}{endpoint}'

    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=5)

        if response.status_code == 401:
            refresh_token = session.get('refresh_token')

            if refresh_token:
                # Le backend attend le refresh_token dans un cookie httpOnly
                print(f"🌺DEBUG : {refresh_token}")
                refresh_response = requests.post(
                    f'{API_URL}/auth/refresh',
                    cookies={'refresh_token': refresh_token},
                    timeout=5
                )

                if refresh_response.status_code == 200:
                    new_token = refresh_response.json().get('access_token')
                    session['token'] = new_token
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.request(method, url, json=data, headers=headers, timeout=5)
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


@app.route('/')
def index():
    """Page d'accueil - redirige vers dashboard si connecté"""
    return render_template('index.html')


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
    total_sessions = len(sessions)
    quiz_count = sum(1 for s in sessions if s.get('type') == 'quiz')
    flashcard_count = sum(1 for s in sessions if s.get('type') == 'flashcard')
    total_correct = 0
    total_questions = 0

    for s in sessions:
        if s.get('score') is not None and s.get('max_score') is not None:
            total_correct += s.get('score', 0)
            total_questions += s.get('max_score', 0)

    accuracy = int((total_correct / total_questions * 100)) if total_questions > 0 else 0
    cards_progress = min(75, flashcard_count * 5)
    quiz_progress = min(100, quiz_count * 10)

    # ****************************
    # TEMPORAIRE POUR DEMODAY
    # ***************************

    # 4. Calculer les données du graphique (7 derniers jours)
    today_dt = datetime.now()
    stats_per_day = {}
    day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

    for i in range(6, -1, -1):
        day = today_dt - timedelta(days=i)
        day_key = day.strftime('%Y-%m-%d')

        # GÉNÉRATION DE FAUSSES DONNÉES pour le rendu visuel (Demoday)
        # On génère un nombre de cartes entre 20 et 60 pour faire de belles vagues
        fake_cards = random.randint(25, 65)
        # Le temps d'étude est lié aux cartes (environ 1.5 min par carte + un bonus)
        fake_time = int(fake_cards * 1.5) + random.randint(5, 15)

        stats_per_day[day_key] = {
            'label': day_names[day.weekday()],
            'cards': fake_cards,
            'time': fake_time
        }

    # On prépare les listes pour Chart.js
    chart_data = {
        'labels': [],
        'cards_created': [],
        'study_time': []
    }

    for key in sorted(stats_per_day.keys()):
        chart_data['labels'].append(stats_per_day[key]['label'])
        chart_data['cards_created'].append(stats_per_day[key]['cards'])
        chart_data['study_time'].append(stats_per_day[key]['time'])

    # 5. Calcul du streak
    # Récupérer tous les jours où l'utilisateur a été actif
    active_days = set()

    for s in sessions:
        created_at = s.get('created_at')
        if created_at:
            day = created_at[:10]
            active_days.add(day)

    # Calcul du streak
    streak = 0
    current_day = datetime.now()

    while True:
        day_str = current_day.strftime('%Y-%m-%d')

        if day_str in active_days:
            streak += 1
            current_day -= timedelta(days=1)
        else:
            break

    # 6. Préparer les stats pour le template
    stats = {
        'cards_generated': flashcard_count,
        'cards_progress': cards_progress,
        'quizzes_created': quiz_count,
        'quiz_progress': quiz_progress,
        'correct_answers': total_correct,
        'accuracy': accuracy,
        'cards_mastered': flashcard_count,
        'study_time': f"{total_sessions * 5}min",
        'streak': streak
    }

    # 7. Rendre le template
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
    user = session.get('user')
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
            'id': s.get('id'),
            'theme_name': theme_name or 'Sans thème',
            'questions_count': s.get('questions_count', 0),
            'score': s.get('score'),
            'max_score': s.get('max_score'),
            'created_at': s.get('created_at'),
        })

    # Plus récent en premier
    quizzes.sort(key=lambda x: x['created_at'] or '', reverse=True)

    return render_template('quizzes.html', quizzes=quizzes, active_view='quiz')


@app.route('/cards-list')
@login_required
def card_list():
    """Page listant toutes les sessions flashcard de l'utilisateur"""

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
                success_theme, theme_data, _ = make_api_request(f'/themes/{theme_id}', token=token)
                if success_theme:
                    theme_name = theme_data.get('name', 'Sans thème')
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
    user = session.get('user')

    print(f"[DEBUG] token = {token}")
    print(f"[DEBUG] user  = {user}")

    try:
        pdf_file = request.files.get('pdf_file')
        session_type = request.form.get('session_type')

        files = {'pdf_file': (pdf_file.filename, pdf_file.stream, pdf_file.mimetype)}
        data = {'session_type': session_type, 'user_id': user.get('id')}
        headers = {'Authorization': f'Bearer {token}'}

        if not pdf_file:
            print(f"DEBUG: no pdf file, {pdf_file}")

        if not session_type:
            print(f"DEBUG: no session type detected {session_type}")

        if not files:
            print(f"DEBUG: no file detected/parse {files}")

        if not data:
            print(f"DEBUG: no data parse {data}")

        if not headers:
            print(f"DEBUG: no header {headers}")

        response = requests.post(
            f'{API_URL}/sessions/create-with-pdf',
            files=files,
            data=data,
            headers=headers,
            timeout=60
        )

        if response.status_code == 401:
            refresh_token = session.get('refresh_token')
            if refresh_token:
                refresh_response = requests.post(
                    f'{API_URL}/auth/refresh',
                    cookies={'refresh_token': refresh_token},
                    timeout=5
                )

                if refresh_response.status_code == 200:
                    new_token = refresh_response.json().get('access_token')
                    session['token'] = new_token
                    headers['Authorization'] = f'Bearer {new_token}'
                    # Rejouer la requête avec le nouveau token
                    response = requests.post(
                        f'{API_URL}/sessions/create-with-pdf',
                        files=files, data=data, headers=headers, timeout=5
                    )
                else:
                    session.clear()
                    return {'error': 'Session expirée'}, 401

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
            },
            timeout=5
        )

        if response.status_code == 200:
            return response.json(), 200
        else:
            return response.json(), response.status_code

    except Exception as e:
        return {'error': str(e)}, 500


# **********************************************
# Routes d'authentification
# **********************************************
@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Proxy vers l'API de login"""
    try:
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=request.json,
            timeout=5
        )

        data = response.json()

        if not data:
            flash('Votre session a expiré, veuillez vous reconnecter', 'warning')
            return redirect(url_for('login'))

        if response.status_code == 200:
            session['user'] = data.get('user')
            session['token'] = data.get('token')
            # Le refresh_token est dans un cookie httpOnly côté backend
            # On le transfère en session Flask pour pouvoir le renvoyer au refresh
            refresh_token = response.cookies.get('refresh_token')
            if refresh_token:
                session['refresh_token'] = refresh_token

        return data, response.status_code
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""

    # Si déjà connecté, rediriger vers dashboard
    if 'token' in session and 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        # Afficher le formulaire d'inscription
        return render_template('register.html')

    # POST : Traiter l'inscription
    try:
        data = request.form

        # Récupérer les données du formulaire
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        # Validation côté serveur
        errors = []

        if not email:
            errors.append("L'email est requis")
        elif '@' not in email:
            errors.append("Email invalide")

        if not password:
            errors.append("Le mot de passe est requis")
        elif len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")

        if password != confirm_password:
            errors.append("Les mots de passe ne correspondent pas")

        if not first_name:
            errors.append("Le prénom est requis")

        if not last_name:
            errors.append("Le nom est requis")

        # Si erreurs, réafficher le formulaire
        if errors:
            return render_template('register.html',
                                   errors=errors,
                                   email=email,
                                   first_name=first_name,
                                   last_name=last_name)

        # Appel API pour créer le compte
        response = requests.post(
            f'{API_URL}/auth/register',
            json={
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name
            },
            timeout=10
        )

        if response.status_code == 201:
            # Inscription réussie
            flash('Compte créé avec succès ! Vous pouvez vous connecter.', 'success')
            return redirect(url_for('login'))

        elif response.status_code == 409:
            # Email déjà utilisé
            return render_template('register.html',
                                   errors=["Cet email est déjà utilisé"],
                                   email=email,
                                   first_name=first_name,
                                   last_name=last_name)

        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('message', error_data.get(
                    'description', 'Erreur lors de la création du compte'))
            except Exception:
                error_msg = f"Erreur serveur (code {response.status_code})"

            return render_template('register.html',
                                   errors=[error_msg],
                                   email=email,
                                   first_name=first_name,
                                   last_name=last_name)

    except requests.exceptions.Timeout:
        return render_template('register.html',
                               errors=["Le serveur met trop de temps à répondre"],
                               email=email,
                               first_name=first_name,
                               last_name=last_name)

    except Exception as e:
        print(f"[ERROR] Erreur inscription: {str(e)}")
        return render_template('register.html',
                               errors=["Erreur serveur, veuillez réessayer"],
                               email=email,
                               first_name=first_name,
                               last_name=last_name)


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


@app.context_processor
def inject_current_year():
    """Injecte l'année courante dans tous les templates"""
    return {'current_year': datetime.now().year}

# en lien avec le modal de fin (session carte) et la sauvegarde des bonnes réponses


@app.route('/api/sessions/<session_id>', methods=['PUT'])
@login_required
def proxy_update_session(session_id):
    """Proxy pour mettre à jour le score d'une session"""
    token = session.get('token')

    try:
        response = requests.put(
            f'http://localhost:5000/api/sessions/{session_id}',
            json=request.json,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=5
        )
        return response.json(), response.status_code

    except Exception as e:
        return {'error': str(e)}, 500

# **********************************************
# Slide de présentation
# **********************************************


@app.route("/presentation")
def presentation():
    return render_template("presentation.html")


# **********************************************
# Lancement de l'application
# **********************************************
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=False)
