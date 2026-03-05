# 🗂️ Models — Couche de données

> Les fondations. Chaque entité de SmartCard vit ici, bien structurée et robuste.

Les modèles définissent le schéma de la base de données via **SQLAlchemy ORM**. Tous héritent de `BaseModel` qui leur offre gratuitement des colonnes communes et des comportements partagés.

---

## 📁 Fichiers

```
Models/
├── tablesSchema.py   → Base SQLAlchemy + Enums (QuestionType, Difficulty, SessionType)
├── baseModel.py      → Classe abstraite parente de tous les modèles
├── userModel.py      → Utilisateur (email, password, prénom, nom)
├── themeModel.py     → Thème issu d'un PDF (nom, mots-clés, description)
├── questionModel.py  → Question (texte, type, difficulté)
├── answerModel.py    → Réponse associée à une question
└── sessionModel.py   → Session d'apprentissage (quiz ou flashcard)
```

---

## 🧱 BaseModel — Ce que chaque modèle hérite

Chaque entité bénéficie automatiquement de :

| Colonne | Type | Description |
|---|---|---|
| `id` | `String(60)` | UUID unique généré automatiquement |
| `created_at` | `DateTime` | Date de création |
| `updated_at` | `DateTime` | Dernière modification (auto-update) |
| `deleted_at` | `DateTime` | Date de suppression logique (soft delete) |

Et de méthodes utilitaires :
- `to_dict()` — Sérialise en JSON (exclut le mot de passe par défaut)
- `soft_delete()` — Suppression logique, les données restent en base
- `is_deleted()` — Vérifie si l'entité est supprimée
- `update_timestamp()` — Met à jour manuellement `updated_at`

---

## 📐 Enums disponibles

```python
QuestionType  →  QUIZ | FLASHCARD
Difficulty    →  EASY | MEDIUM | HARD
SessionType   →  QUIZ | FLASHCARD
```

---

## 🔗 Relations entre entités

```
User
 └── Theme (1 user → N thèmes)
      └── Question (1 thème → N questions)
           └── Answer  (1 question → N réponses)

Session (regroupe N questions pour une séance d'étude)
```

---

## 💡 Design choice

Le **soft delete** est un choix délibéré : supprimer une question ou un thème ne l'efface pas réellement de la base. Cela préserve l'historique des sessions passées et permet une éventuelle restauration. Toutes les requêtes filtrent `deleted_at IS NULL` par défaut.
