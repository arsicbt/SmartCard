# 🗄️ Persistence — Couche d'accès aux données

> Une seule interface pour parler à la base de données. Propre, sécurisée, réutilisable.

`DBStorage` est le **Repository** central de SmartCard. Inspiré du pattern HBNB (Holberton), il encapsule toutes les interactions avec SQLAlchemy et expose une API unifiée pour le reste de l'application.

---

## 📁 Fichiers

```
Persistence/
├── __init__.py
└── DBStorage.py   → Gestionnaire principal (singleton)
```

---

## 🔧 Méthodes disponibles

### Opérations de base (CRUD)

| Méthode | Description |
|---|---|
| `all(cls)` | Récupère tous les objets d'une classe |
| `get(cls, id)` | Récupère un objet par son ID |
| `new(obj)` | Ajoute un objet à la session |
| `save()` | Commit (avec rollback automatique en cas d'erreur) |
| `delete(obj)` | Soft delete par défaut, hard delete optionnel |
| `reload()` | Recrée les tables et rouvre la session |
| `close()` | Ferme la session proprement |

### Recherche avancée

| Méthode | Description |
|---|---|
| `get_by_email(cls, email)` | Recherche par email (normalisé lowercase) |
| `filter_by(cls, **filters)` | Filtre multi-critères dynamique |
| `count(cls, **filters)` | Compte les entités selon critères |

---

## 🗃️ Compatibilité bases de données

```python
# SQLite (développement — zéro config)
DATABASE_URL=sqlite:///smartcard.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@host:5432/smartcard
```

Le moteur s'adapte automatiquement selon la variable d'environnement `DATABASE_URL`.

---

## 🔐 Sécurité intégrée

- **Requêtes préparées** SQLAlchemy → protection native contre les injections SQL
- **Soft delete par défaut** → les données supprimées restent en base pour l'audit
- **Gestion des transactions** → rollback automatique en cas d'exception
- **Context manager** `with storage.transaction()` pour les opérations atomiques
- **Sessions thread-safe** via `scoped_session` (compatible Flask multi-thread)

---

## 💡 Utilisation

```python
from Persistence.DBStorage import storage
from Models.userModel import User

# Récupérer un user
user = storage.get(User, user_id)

# Filtrer
users = storage.filter_by(User, email="test@example.com")

# Créer
user = User(email="new@example.com", ...)
storage.new(user)
storage.save()

# Supprimer (soft)
storage.delete(user)
storage.save()
```
