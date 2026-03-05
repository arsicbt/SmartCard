# 🎨 Frontend — Interface utilisateur

> Ce que l'utilisateur voit et touche. Simple, fonctionnel, et agréable.

Le frontend est une application **Flask** indépendante qui communique avec le backend via des appels HTTP. Elle gère le rendu des templates Jinja2 et sert de proxy pour les opérations complexes (upload de fichiers, refresh token).

---

## 📁 Structure

```
Frontend/
├── front.py              → Application Flask (port 3000) + toutes les routes
├── static/
│   ├── css/style.css     → Styles globaux
│   └── js/main.js        → Interactions dynamiques (quiz, flashcards, graphiques)
└── templates/
    ├── base.html         → Layout principal (héritage Jinja2)
    ├── login.html        → Page de connexion
    ├── dashboard.html    → Tableau de bord avec statistiques
    ├── session.html      → Création d'une session (upload PDF)
    ├── cards.html        → Mode flashcards (recto/verso interactif)
    ├── cards-list.html   → Galerie des sessions flashcard
    ├── quizz.html        → Mode quiz (QCM avec score final)
    ├── quizzes.html      → Galerie des sessions quiz
    ├── components/       → Composants réutilisables (header, sidebar, footer…)
    └── macros/           → Macros Jinja2 (formulaires, stats)
```

---

## 🗺️ Routes disponibles

| Route | Description |
|---|---|
| `/` | Redirection → dashboard ou login |
| `/login` | Page de connexion |
| `/dashboard` | Tableau de bord (stats + graphique 7 jours) |
| `/session` | Création d'une session (upload PDF) |
| `/cards/<id>` | Lecteur de flashcards |
| `/cards-list` | Historique des sessions flashcard |
| `/quiz/<id>` | Quiz interactif |
| `/quizzes-list` | Historique des sessions quiz |

---

## 🔄 Communication avec le Backend

Le frontend ne touche jamais directement la BDD — tout passe par l'API :

```python
# Appel simplifié
success, data, status = make_api_request('/themes', method='GET', token=token)
```

Le **refresh automatique du token** est géré de façon transparente : si une requête reçoit un `401`, le frontend tente de renouveler l'access token avant de réessayer.

---

## 🔑 Authentification côté front

- La session Flask stocke `user`, `token` et `refresh_token`
- Le décorateur `@login_required` protège toutes les routes sensibles
- À la déconnexion, `session.clear()` efface tout proprement

---

## 💻 Lancement

```bash
cd Frontend
python front.py   # → http://localhost:3000
```

> ⚠️ Le backend doit tourner sur le port 5000 avant de lancer le frontend.
