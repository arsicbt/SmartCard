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

> **POINT DE BLOCAGE — opération destructive (TRANCHÉ).**
> `--reset` exécute `Base.metadata.drop_all()` : **toutes les données existantes sont perdues** (utilisateurs, thèmes, questions, réponses, sessions). S'il existe une base contenant des données à conserver (ex. environnement déployé), il faut une vraie migration (sauvegarde + recréation + réimport, ou mise en place d'Alembic).

**Décision validée par l'utilisateur (app non déployée) :** la base SQLite locale a été recréée. Schéma vérifié après recréation — la table `users` contient désormais :
```
first_name, last_name, email, password, name, is_admin, last_login_at, id, created_at, updated_at, deleted_at
```
Les colonnes `is_verified` et `verification_token` ont bien disparu. Les 5 tables (`users`, `themes`, `questions`, `answers`, `sessions`) sont recréées et le Backend redémarre sans erreur.

---

## [Tâche 5.1] Suppression des services CRUD morts et cassés `coreServices.py` et `cardsServices.py`

**Fichier(s) modifié(s) :**
- `Backend/Services/coreServices.py` (supprimé)
- `Backend/Services/cardsServices.py` (supprimé)
- `Backend/Services/README.md` (mise à jour de l'arborescence)

**Avant :**
- `coreServices.py` définissait une classe `coreServices` censée servir de parent CRUD abstrait, mais ses méthodes utilisaient une API de stockage inexistante et n'étaient appelées par aucune route.
- `cardsServices.py` héritait de `coreServices` et n'était importé nulle part dans l'application (`app.py` ne l'enregistre pas).
- Recherche `coreServices|cardsServices|CardsServices` sur tout le Backend : seules références = ces deux fichiers entre eux + la documentation `Services/README.md`.

**Après :**
- Les deux fichiers sont supprimés.
- `Services/README.md` ne liste plus ces fichiers et signale explicitement leur suppression.

**Justification :**
Code mort et cassé, totalement redondant avec le pattern Repository déjà présent dans `Persistence/DBStorage.py` (qui centralise tout le CRUD : `get`, `all`, `filter_by`, `new`, `save`, `delete`, `transaction`). Conserver deux implémentations CRUD divergentes nuit à la lisibilité et au critère « pas de doublon » de l'audit (CP5/CP7).

**Impact :**
- Aucune route ni aucun service actif n'importait ces fichiers : suppression sans risque fonctionnel.
- L'application démarre toujours correctement (Backend API `RUNNING`).

---

## [Tâche 5.4] Suppression du service d'authentification mort et cassé `authServices.py`

**Fichier(s) modifié(s) :**
- `Backend/Services/authServices.py` (supprimé)
- `Backend/Services/README.md` (note de suppression)

**Avant :**
`authServices.py` définissait une classe `AuthService` avec `register()` et `login()`. Ce code était :
- **mort** : importé nulle part (recherche `authServices|AuthService` = aucun import) ;
- **cassé** : `register()` construisait `User(email=, password=, name=)` sans `first_name` / `last_name` (colonnes `nullable=False`) → échec garanti ;
- **cassé** : `login()` et `register()` appelaient `TokenManager.create_access_token(...)`, méthode qui **n'existe pas** (`Utils/tokenSecurity.py` expose `generate_tokens()`). Recherche `create_access_token` sur tout le Backend : présent **uniquement** dans `authServices.py`.

**Après :**
- Fichier supprimé.
- La logique d'authentification réelle et fonctionnelle est déjà répartie ailleurs :
  - **Émission des tokens** : `Utils/tokenSecurity.py` → `token_manager.generate_tokens()`, déjà utilisée par `Api/authRoutes.py`.
  - **Vérification d'identité** : `Services/usersServices.py` → `UserService.authenticate()`.

**Justification :**
Tâche 5.4 demandait de « fusionner la logique utile dans `tokenSecurity.py` et/ou `usersServices.py` puis supprimer ». Après analyse, `authServices.py` ne contenait **aucune logique utile absente ailleurs** : `authRoutes.py` fait déjà mieux (gestion `first_name`/`last_name`, refresh token, `generate_tokens`). La « correction » de `create_access_token` → `generate_tokens` demandée par l'audit était sans objet une fois ce doublon cassé supprimé, l'appel correct existant déjà dans `authRoutes.py`. Suppression du doublon (CP5/CP7).

**Impact :**
- Aucune régression : flux login/register inchangé (assuré par `authRoutes.py` + `UserService.authenticate`).
- Surface de code mort réduite.

---

## [Tâche 5.2] Réparation de `UserService` (références classe) et branchement dans `userRoutes.py`

**Fichier(s) modifié(s) :**
- `Backend/Services/usersServices.py`
- `Backend/Api/userRoutes.py`

**Avant :**
- `UserService` était **cassé** : il appelait les méthodes de `DBStorage` en passant des **chaînes** comme classe — `storage.filter_by('User', ...)`, `storage.get('User', ...)`, `storage.all('User')`. Or `DBStorage` exécute `self.__session.query(cls)` et attend la **classe** `User`, pas la chaîne `'User'` → toute requête échouait.
- `Api/userRoutes.py` n'utilisait pas du tout `UserService` : la logique métier (unicité email, validation, soft delete) était écrite en dur dans les routes, et le `PUT` recopiait n'importe quel attribut via `setattr` (`hasattr`), exposant des champs sensibles (ex. `is_admin`).

**Après :**
- `usersServices.py` : toutes les références chaîne remplacées par la classe `User` (déjà importée) — `filter_by(User, ...)`, `get(User, ...)`, `all(User)`.
- `userRoutes.py` réécrit pour **déléguer** à `UserService` (instancié une fois au niveau module) : `get_all_users`, `get_user_by_id`, `create_user`, `update_user`, `delete_user`. Les décorateurs d'autorisation existants (`@admin_required`, `@auth_required`) et la validation HTTP simple (présence des champs, JSON) restent dans la route.

**Justification :**
Réparation d'un service cassé + respect de l'architecture en couches visée (les routes valident le HTTP, les services portent la logique métier) — CP5/CP6/CP7.

**Amélioration de sécurité :** le `PUT` passe désormais par `UserService.update_user`, qui restreint les champs modifiables à `updatable_fields = ['first_name', 'last_name', 'name']`. Un utilisateur ne peut plus modifier `is_admin`, `email` ou `password` via cette route (alors que l'ancien `setattr` générique le permettait).

**Impact :**
- Test fonctionnel (smoke test) validé : `POST /api/users/` → `201` à la création ; doublon d'email → `400 « Un utilisateur avec cet email existe déjà »` (preuve que `filter_by(User, ...)` fonctionne maintenant). Utilisateur de test supprimé après vérification.
- L'application démarre correctement.

---

## [Tâche 5.3] Réparation de `QuizzService`, migration du matching depuis `sessionRoutes`, branchement de `submit_quiz`

**Fichier(s) modifié(s) :**
- `Backend/Services/questionServices.py`
- `Backend/Api/sessionRoutes.py`

**Avant :**
- `QuizzService` était **cassé** de la même façon que `UserService` : appels `storage.get('Theme', ...)`, `storage.filter_by('Question', ...)`, `storage.get('Session', ...)`, `storage.filter_by('Answer', ...)` avec des **chaînes** au lieu des classes.
- `Api/sessionRoutes.py` (`create_session_with_pdf`) contenait **en dur** la logique de matching de similarité (appels directs à `SimilarityService.find_matching_theme` et `calculate_text_similarity`), dupliquant une responsabilité métier qui devait vivre dans le service.
- La méthode métier `QuizzService.submit_quiz()` (qui calcule le score **et** incrémente `times_used`/`times_correct` des questions) n'était **branchée à aucune route** : impossible de soumettre un quiz via l'API.

**Après :**
- `questionServices.py` : toutes les références chaîne remplacées par les classes (`Theme`, `Question`, `Answer`, `Session`) ; ajout des imports `from Models.themeModel import Theme` et `from Services.similarityService import SimilarityService`.
- Deux méthodes ajoutées à `QuizzService` pour **centraliser le matching** (logique déplacée verbatim depuis la route) :
  - `find_matching_theme_for_user(user_id, pdf_keywords, threshold=0.4)` → cherche un thème existant de l'utilisateur correspondant aux mots-clés du PDF.
  - `match_generated_to_existing_questions(generated_questions, theme_id, threshold=0.4)` → renvoie `(matched_ids, unmatched_generated)`.
- `sessionRoutes.py` : la route `create_session_with_pdf` appelle désormais ces deux méthodes (import `SimilarityService` retiré de la route, remplacé par `QuizzService`). L'orchestration du pipeline PDF (extraction, appels IA, persistance via `_create_questions_from_generated`) reste dans la route.
- Nouvelle route `POST /api/sessions/<session_id>/submit` (`submit_quiz`) qui délègue à `QuizzService.submit_quiz`, avec vérification de propriété de la session (propriétaire ou admin) calquée sur `update_session`.

**Justification :**
Réparation d'un service cassé + suppression de la duplication de logique métier entre la route et le service (la route faisait le matching « à la main ») + activation d'une fonctionnalité métier existante mais non exposée. CP5/CP6/CP7.

**Impact :**
- La logique de matching n'existe plus qu'à **un seul endroit** (`QuizzService`), supprimant le risque de divergence.
- `POST /api/sessions/<id>/submit` permet désormais de terminer un quiz, calculer le score et **mettre à jour les statistiques des questions** (`times_used` / `times_correct`) — pré-requis de la Tâche 2.4.
- Compilation OK sur tout le Backend ; le serveur démarre sans erreur.
- **À valider fonctionnellement par l'utilisateur :** le pipeline complet `create-with-pdf` dépend d'un upload PDF réel + de l'API Groq, non testable automatiquement ici. La logique de matching ayant été déplacée à l'identique, aucun changement de comportement n'est attendu.

---

## [Tâche 2.1] Enregistrement de la dernière connexion (`last_login_at`)

**Fichier(s) modifié(s) :**
- `Backend/Models/userModel.py`
- `Backend/Api/authRoutes.py`

**Avant :**
- Le modèle `User` exposait la méthode `update_last_login()` et la colonne `last_login_at`, mais **aucune route ne l'appelait** : `last_login_at` restait donc `NULL` à vie après l'inscription.
- `update_last_login()` affectait `datetime.utcnow()` (objet `datetime`) à `last_login_at`, alors que la colonne est de type `String` — incohérence de type reposant sur une coercion implicite du driver SQLite.

**Après :**
- `userModel.py` : `update_last_login()` stocke désormais une chaîne ISO 8601 (`datetime.utcnow().isoformat()`), cohérente avec le type `String` de la colonne et avec la sérialisation `to_dict()`.
- `authRoutes.py` (`login`) : après vérification réussie du mot de passe, la route appelle `user.update_last_login()` puis `storage.save()`.

**Justification :**
Activation d'une fonctionnalité métier existante mais non branchée + suppression d'une incohérence de type latente. CP5/CP6.

**Impact :**
- Smoke test validé : à l'inscription `last_login_at = None` ; après `POST /api/auth/login`, la réponse renvoie `last_login_at = "2026-06-30T..."` (chaîne ISO). Utilisateur de test supprimé (hard delete) après vérification.
- Aucune migration de schéma nécessaire (le type de colonne `String` est inchangé).
- **Alternative signalée (non appliquée — destructive) :** aligner `last_login_at` sur le type `DateTime` (comme `created_at`/`updated_at`) serait plus homogène mais impose une recréation de table (pas d'Alembic). Conservé en `String` pour rester non destructif.

---

## [Tâche 2.2] Persistance de l'explication (`explanation`) des questions générées par l'IA

**Fichier(s) modifié(s) :**
- `Backend/Api/sessionRoutes.py`

**Avant :**
- L'IA (Groq) génère bien un champ `explanation` pour chaque question de QUIZ (cf. `Services/pdfAnalysisService.py`, prompt : `"explanation": "Brief explanation of why the correct answer is correct"`).
- Or `_create_questions_from_generated()` construisait l'objet `Question(...)` **sans** transmettre `explanation` → l'explication générée était systématiquement **perdue**, alors que la colonne `Question.explanation` existe et que `Api/questionRoutes.py` la persiste déjà lors d'une création manuelle.

**Après :**
- Ajout de `explanation=q_data.get('explanation')` à la construction de `Question` dans `_create_questions_from_generated()`.

**Justification :**
Correction d'une perte de donnée : la colonne et la donnée source existaient, seul le branchement manquait. Cohérence avec `questionRoutes.create_question` qui persiste déjà ce champ. CP5/CP6.

**Impact :**
- Les questions de QUIZ créées via le pipeline PDF conservent désormais leur explication.
- `q_data.get('explanation')` (et non `[...]`) : si l'IA n'en fournit pas, la valeur reste `None` (colonne `nullable=True`) — aucun risque de `KeyError`.
- **À valider fonctionnellement par l'utilisateur :** dépend d'un upload PDF réel + API Groq.

---

## [Tâche 2.3] Tri des réponses par `order_position` à la sérialisation

**Fichier(s) modifié(s) :**
- `Backend/Api/answerRoutes.py`

**Avant :**
- `GET /api/answers/question/<question_id>` renvoyait `storage.filter_by(Answer, question_id=...)` **sans tri**, donc dans un ordre non garanti par la base.
- La colonne `Answer.order_position` existe pourtant explicitement « pour l'ordre d'affichage (pour les quiz) » (docstring du modèle) et est renseignée à la création (`order_position=ans_idx`).

**Après :**
- La liste des réponses est triée par `order_position` avant sérialisation (`sorted(..., key=lambda a: a.order_position or 0)`), garde incluse contre une valeur `None`.

**Justification :**
L'ordre d'affichage des réponses doit être déterministe et conforme à l'intention du modèle. Sans tri, l'ordre dépendait du moteur de base. CP5/CP6.

**Impact :**
- L'endpoint renvoie désormais les réponses dans l'ordre `order_position` croissant.
- Aucune autre route ne sérialisait les réponses (vérifié) : changement localisé, sans effet de bord.

---

## [Tâche 2.4] Activation de la soumission de quiz — *déjà couverte par la Tâche 5.3*

La mise à jour des statistiques de questions (`times_used` / `times_correct`) via `QuizzService.submit_quiz` a été branchée à la route `POST /api/sessions/<id>/submit` lors de la **Tâche 5.3** (voir entrée correspondante). Aucune action supplémentaire requise pour la Tâche 2.4.

---
