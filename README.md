# 🧠 SmartCard — Portfolio Project

> *Transformez n'importe quel PDF en session d'apprentissage interactive. En quelques secondes.*

**SmartCard** est une application web full-stack qui génère automatiquement des **flashcards** et des **quiz** à partir de documents PDF, grâce à l'IA. Téléchargez votre cours, choisissez votre mode d'apprentissage, et c'est parti !

---

## ✨ Fonctionnalités

| Feature | Description |
|---|---|
|  **Upload PDF** | Analyse automatique du contenu et détection du thème |
|  **Flashcards** | Mode recto/verso pour mémoriser les concepts clés |
|  **Quiz** | QCM générés par IA avec niveaux de difficulté |
|  **Dashboard** | Suivi de progression et statistiques de session |
|  **Auth JWT** | Connexion sécurisée avec access + refresh tokens |

---

## ⚙️ Architecture

```
SmartCard/
├── Backend/         → API REST Flask (port 5000)
│   ├── Api/         → Routes & endpoints
│   ├── Models/      → Entités SQLAlchemy
│   ├── Services/    → Logique métier & IA (Groq)
│   ├── Utils/       → Sécurité (JWT, bcrypt, sanitization)
│   └── Persistence/ → Couche d'accès BDD (DBStorage)
│
└── Frontend/        → Application Flask (port 3000)
    ├── front.py     → Routes & proxy vers l'API
    ├── templates/   → Jinja2 HTML templates
    └── static/      → CSS & JavaScript
```

---

## 👋🏼Vous voulez essayez ?

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement (.env)
GROQ_API_KEY=your_key_here
JWT_SECRET_KEY=your_secret
DATABASE_URL=sqlite:///smartcard.db

# Lancer le backend
cd Backend && python app.py        # → http://localhost:5000

# Lancer le frontend (autre terminal)
cd Frontend && python front.py     # → http://localhost:3000
```

---

## 💻 Stack technique

**Backend :** Python · Flask · SQLAlchemy · PyJWT · bcrypt · PyPDF2 · Groq API (LLaMA 3.3-70b)  
**Frontend :** Flask · Jinja2 · HTML/CSS · JavaScript  
**Base de données :** SQLite (développement) · PostgreSQL (production-ready)

---

## 👩‍💻 Auteure

Projet portfolio réalisé par **Arsinoé** — premier projet full-stack from scratch.
