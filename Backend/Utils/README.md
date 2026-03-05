# 🔐 Utils — Sécurité transversale

> Parce qu'une app bien sécurisée, c'est une app qui dure.

Le dossier `Utils` regroupe tous les outils de sécurité utilisés à travers le backend. Ces modules sont indépendants et peuvent être utilisés dans n'importe quel service ou route.

---

## 📁 Fichiers

```
Utils/
├── tokenSecurity.py      → Génération et décodage des JWT
├── passwordSecurity.py   → Hachage et vérification des mots de passe
├── authVerification.py   → Décorateurs de protection des routes
└── inputSecurity.py      → Validation et sanitisation des entrées
```

---

## 🔑 TokenSecurity — Gestion des JWT

Deux tokens pour une sécurité renforcée :

| Token | Durée | Rôle |
|---|---|---|
| **Access token** | 1 heure | Autoriser les requêtes API |
| **Refresh token** | 7 jours | Renouveler l'access token sans reconnexion |

```python
from Utils.tokenSecurity import token_manager

# Générer une paire de tokens
access, refresh = token_manager.generate_tokens(user_id, email)

# Décoder
payload = token_manager.decode_access_token(token)  # → None si expiré
```

Le refresh token est stocké dans un **cookie httpOnly** (inaccessible depuis JavaScript) pour se protéger des attaques XSS.

---

## 🔒 PasswordSecurity — Hachage bcrypt

```python
from Utils.passwordSecurity import PasswordManager

hashed = PasswordManager.hash_password("mon_mot_de_passe")
is_valid = PasswordManager.verify_password("mon_mot_de_passe", hashed)
```

Utilise **bcrypt** avec salt automatique. Aucun mot de passe n'est jamais stocké en clair.

---

## 🛡️ AuthVerification — Décorateurs de routes

Protège les endpoints en une ligne :

```python
@app.route('/api/resource')
@auth_required          # Vérifie le JWT → injecte request.current_user
def protected_route():
    user = request.current_user
    ...

@app.route('/api/admin/resource')
@admin_required         # Réservé aux utilisateurs is_admin=True
def admin_route():
    ...
```

---

## 🧹 InputSecurity — Validation des entrées

Sanitisation systématique avant toute insertion en base :
- Nettoyage des caractères dangereux
- Validation du format email
- Vérification des longueurs minimales/maximales
- Protection contre les injections via les champs texte

---

## 💡 Bonne pratique

Ces modules ne dépendent d'aucun autre module interne — ils peuvent être testés unitairement de façon totalement isolée. 
