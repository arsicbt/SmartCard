# 🧠 Services — Logique métier & IA

> C'est ici que la magie opère. PDF entrant, flashcards sortantes.

La couche Services contient toute la logique métier de SmartCard, en particulier le **pipeline d'analyse PDF** qui transforme un document brut en contenu pédagogique structuré via l'IA.

---

## 📁 Fichiers

```
Services/
├── coreServices.py        → CRUD de base abstrait (parent des autres services)
├── cardsServices.py       → Service dédié aux flashcards
├── authServices.py        → Logique d'authentification
├── usersServices.py       → Gestion des utilisateurs
├── questionServices.py    → Gestion des questions
├── pdfAnalysisService.py  → Pipeline PDF → IA → Questions
└── similarityService.py   → Calcul de similarité texte (TF-IDF / Jaccard)
```

---

## ✨ PDFAnalysisService — Le cœur du projet

Pipeline en 3 étapes déclenché à chaque upload de PDF :

```
PDF  →  [1. Extraction texte]  →  [2. Analyse thème Groq]  →  [3. Génération questions Groq]
                                                                         ↓
                                                              Quiz ou Flashcards
```

### Étape 1 — Extraction (`extract_text_from_pdf`)
Lit toutes les pages du PDF via **PyPDF2** et concatène le texte.

### Étape 2 — Analyse du thème (`analyze_theme_with_groq`)
Envoie les 4 000 premiers caractères à **Groq (LLaMA 3.3-70b)** et récupère en JSON :
- `theme_name` — Nom du thème détecté
- `keywords` — 5 à 10 mots-clés
- `description` — Description courte (max 200 caractères)

### Étape 3 — Génération de questions (`generate_questions_from_pdf`)
Génère jusqu'à **10 questions** adaptées au mode choisi :
- **QUIZ** → QCM avec 4 choix, 1 correcte, explication, niveau de difficulté
- **FLASHCARD** → Paire question/réponse concise

> 💬 Le modèle détecte automatiquement la langue du document et génère dans la même langue.

---

## 📐 SimilarityService — Algorithme de matching

Utilisé pour éviter les doublons et suggérer des thèmes existants :

| Méthode | Algorithme | Usage |
|---|---|---|
| `calculate_text_similarity` | Coefficient de Jaccard | Comparer deux textes |
| `calculate_keyword_overlap` | Intersection de sets | Comparer des listes de mots-clés |
| `find_matching_questions` | Jaccard + seuil (0.4) | Retrouver des questions similaires |
| `find_matching_theme` | Overlap + seuil (0.4) | Suggérer un thème existant |

---

## 🔧 Configuration requise

```env
GROQ_API_KEY=your_key_here   # Obligatoire pour PDFAnalysisService
```

Le service lève une `ValueError` au démarrage si la clé est absente — pas de surprise en production.
