# 🔌 Api — Routes & Endpoints REST

> L'interface publique du backend. Ce que le frontend (et le monde extérieur) peut appeler.

Chaque fichier de ce dossier définit un **Blueprint Flask** qui regroupe les routes d'une ressource. Ils sont tous enregistrés dans `app.py` au démarrage.

---

## 📁 Fichiers

```
Api/
├── authRoutes.py      → /api/auth/*     — Login, logout, refresh, profil
├── userRoutes.py      → /api/users/*    — CRUD utilisateurs
├── themeRoutes.py     → /api/themes/*   — Gestion des thèmes
├── questionRoutes.py  → /api/questions/* — Gestion des questions
├── answerRoutes.py    → /api/answers/*  — Gestion des réponses
└── sessionRoutes.py   → /api/sessions/* — Sessions d'apprentissage + pipeline PDF
```

---

## 📋 Référence des endpoints

### 🔐 Auth (`/api/auth`)

| Méthode | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/login` | ❌ | Connexion → retourne JWT + cookie refresh |
| `POST` | `/refresh` | ❌ | Renouvelle l'access token |
| `POST` | `/logout` | ❌ | Supprime les cookies JWT |
| `GET` | `/me` | ✅ | Retourne l'utilisateur connecté |
| `POST` | `/admin` | ✅ Admin | Crée un compte administrateur |

### 👤 Users (`/api/users`)

| Méthode | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/` | ✅ Admin | Liste tous les utilisateurs |
| `POST` | `/` | ❌ | Inscription |
| `GET` | `/<id>` | ✅ | Détail utilisateur |
| `PUT` | `/<id>` | ✅ | Mise à jour |
| `DELETE` | `/<id>` | ✅ | Suppression (soft delete) |

### 📚 Sessions (`/api/sessions`)

| Méthode | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/create-with-pdf` | ✅ | ✨ Pipeline complet : PDF → thème → questions → session |
| `GET` | `/user/<user_id>` | ✅ | Sessions d'un utilisateur |
| `GET` | `/<id>` | ✅ | Détail d'une session |
| `PUT` | `/<id>` | ✅ | Mise à jour du score |
| `DELETE` | `/<id>` | ✅ | Suppression d'une session |

---

## 🔄 Format des réponses

Toutes les réponses suivent le format JSON standard :

```json
// Succès
{ "message": "...", "data": { ... } }

// Erreur
{ "error": "Description de l'erreur" }
```

Les codes HTTP utilisés : `200`, `201`, `400` (bad request), `401` (non autorisé), `404` (not found), `500` (erreur serveur).

---

## 🚀 Pipeline PDF (endpoint principal)

```
POST /api/sessions/create-with-pdf
Content-Type: multipart/form-data

Paramètres:
  pdf_file      → Fichier PDF
  session_type  → "QUIZ" ou "FLASHCARD"
  user_id       → ID de l'utilisateur

Retourne:
  session_id, theme créé, questions générées
```
