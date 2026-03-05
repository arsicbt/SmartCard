# ⚙️ Backend — API REST SmartCard

> Le cerveau de l'application. Une API Flask propre, sécurisée, et prête à scaler.

Le backend expose une **API REST** complète qui gère l'authentification, la gestion des utilisateurs, le traitement des PDFs et la génération de contenu éducatif via l'IA.

---

## 📁 Structure

```
Backend/
├── app.py          → Point d'entrée Flask, enregistrement des blueprints
├── config.py       → Configuration de l'application
├── init_db.py      → Initialisation et migration de la base de données
│
├── Api/            → Endpoints REST (routes)
├── Models/         → Modèles de données SQLAlchemy
├── Services/       → Logique métier & services IA
├── Utils/          → Outils de sécurité transversaux
└── Persistence/    → Couche d'accès aux données (DBStorage)
```

---

## 🔌 Endpoints disponibles

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Connexion utilisateur |
| `POST` | `/api/auth/refresh` | Renouvellement du token |
| `GET` | `/api/auth/me` | Utilisateur connecté |
| `GET/POST` | `/api/users` | Gestion des utilisateurs |
| `GET/POST` | `/api/themes` | Gestion des thèmes |
| `GET/POST` | `/api/questions` | Gestion des questions |
| `GET/POST` | `/api/answers` | Gestion des réponses |
| `GET/POST` | `/api/sessions` | Sessions d'apprentissage |
| `POST` | `/api/sessions/create-with-pdf` | ✨ Pipeline complet PDF → quiz/cards |

---

## 🚀 Lancement

```bash
cd Backend

# Variables d'environnement requises
export GROQ_API_KEY="your_groq_key"
export JWT_SECRET_KEY="your_jwt_secret"
export DATABASE_URL="sqlite:///smartcard.db"

# Initialiser la base de données
python init_db.py

# Démarrer le serveur
python app.py   # → http://localhost:5000
```

---

## 🔑 Sécurité

- Authentification par **JWT** (access token 1h + refresh token 7j via cookie httpOnly)
- Mots de passe hashés avec **bcrypt**
- Soft delete sur toutes les entités (données jamais perdues)
- Requêtes préparées SQLAlchemy (protection injection SQL)
- Validation et sanitisation des entrées utilisateur

---

## 🤖 Intelligence Artificielle

L'API communique avec **Groq (LLaMA 3.3-70b)** pour :
1. Détecter automatiquement le thème d'un PDF
2. Générer des questions de quiz (QCM avec 4 choix)
3. Générer des flashcards recto/verso

Le modèle respecte la langue du document source (français ou anglais).
