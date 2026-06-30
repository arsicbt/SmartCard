# CHANGELOG AUDIT — SmartCards

> Journal des modifications de l'audit de nettoyage et de branchement des composants morts.
> Chaque entrée suit le format : Fichier(s) / Avant / Après / Justification / Impact.
> Ce document nourrit le dossier de certification RNCP DWWM (CP5, CP6, CP7).

---

## [Tâche 1.1] Suppression des champs morts `verification_token` et `is_verified` du modèle `User`

**Fichier(s) modifié(s) :**
- `Backend/Models/userModel.py`
- `Backend/Services/usersServices.py`

**Avant :**

`Backend/Models/userModel.py` — déclarait deux colonnes liées à un flux de vérification d'email inexistant :
```python
# Vérification email
is_verified = Column(Boolean, default=False, nullable=False)
is_admin = Column(Boolean, default=False, nullable=False)
verification_token = Column(String(255), nullable=True)
last_login_at = Column(String, nullable=True)
```
La docstring de la classe listait `is_verified` et `verification_token`, et la fabrique `validate_and_create()` passait `is_verified=False` à la construction de l'objet `User`.

`Backend/Services/usersServices.py` — exposait `is_verified` comme champ modifiable via l'API :
```python
updatable_fields = ['first_name', 'last_name', 'name', 'is_verified']
```

**Après :**

`Backend/Models/userModel.py` — colonnes mortes supprimées ; seuls `is_admin` et `last_login_at` restent :
```python
# Statut & activité
is_admin = Column(Boolean, default=False, nullable=False)
last_login_at = Column(String, nullable=True)
```
Docstring de classe nettoyée (lignes `is_verified` / `verification_token` retirées) et `is_verified=False` retiré de l'appel `User(...)` dans `validate_and_create()`.

`Backend/Services/usersServices.py` :
```python
updatable_fields = ['first_name', 'last_name', 'name']
```

**Justification :**
Aucun flux de vérification d'email n'existe dans l'application (pas d'envoi de mail, pas de route de confirmation). Ces deux champs n'étaient jamais lus, et `is_verified` n'était jamais mis à jour après sa valeur par défaut. De plus, l'exposer dans `updatable_fields` permettait à un utilisateur de modifier son propre statut de vérification — incohérence supplémentaire. Conformité audit : suppression de code mort (CP5/CP7).

**Impact :**
- Le schéma de la table `users` ne contient plus les colonnes `is_verified` et `verification_token`.
- La sérialisation `to_dict()` (générique, basée sur `self.__table__.columns`) n'expose plus ces champs automatiquement — aucune modification de `to_dict()` n'a été nécessaire.
- Aucune route ni aucun test ne dépendait de ces champs (vérifié par recherche `verification_token|is_verified` sur tout le dépôt : seules les 4 occurrences ci-dessus existaient, plus le prompt d'audit lui-même).
- L'application démarre toujours correctement (Backend API + Frontend) et `init_db.py` recrée les tables sans erreur.

---

## Procédure de migration du schéma (Tâche 1)

**Aucun système de migration (Alembic) n'est en place dans le projet.** Le schéma est créé/recréé par `Backend/init_db.py` via `Base.metadata.create_all(engine)`. La base par défaut est SQLite (`Backend/smartcard.db`, surchargée par la variable d'environnement `DATABASE_URL`).

SQLite ne supporte pas proprement le `DROP COLUMN` sur d'anciennes versions ; la suppression de colonnes implique donc de **recréer les tables**. Procédure exacte :

```bash
cd Backend
# 1. Supprime toutes les tables (demande une confirmation interactive : taper "oui")
python init_db.py --reset
# 2. Recrée toutes les tables à partir des modèles à jour
python init_db.py
```

> **POINT DE BLOCAGE À VALIDER — opération destructive.**
> `--reset` exécute `Base.metadata.drop_all()` : **toutes les données existantes sont perdues** (utilisateurs, thèmes, questions, réponses, sessions). En développement sur la base SQLite locale, c'est acceptable. S'il existe une base contenant des données à conserver (ex. environnement déployé), il faut une vraie migration (sauvegarde + recréation + réimport, ou mise en place d'Alembic). **Je ne lance pas `--reset` automatiquement et j'attends votre décision sur ce point.**

---
