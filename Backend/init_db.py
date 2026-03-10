"""Script d'initialisation de la base de données SmartCard."""
import sys
import os
import importlib.util

# ─────────────────────────────────────────────────────────────
# Chargement manuel de tablesSchema SANS passer par Models/__init__.py
# Cela évite la chaîne circulaire :
# Models/__init__ → userModel → Utils → authVerification → Persistence → DBStorage → Models
# ─────────────────────────────────────────────────────────────
backend_dir = os.path.dirname(os.path.abspath(__file__))


def _load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Charger tablesSchema directement (sans Models/__init__.py)
tables = _load_module(
    "Models.tablesSchema",
    os.path.join(backend_dir, "Models", "tablesSchema.py")
)
Base = tables.Base

# Charger chaque modèle pour qu'il s'enregistre sur Base.metadata
for model_name, filename in [
    ("Models.baseModel",     "Models/baseModel.py"),
    ("Models.userModel",     "Models/userModel.py"),
    ("Models.themeModel",    "Models/themeModel.py"),
    ("Models.questionModel", "Models/questionModel.py"),
    ("Models.answerModel",   "Models/answerModel.py"),
    ("Models.sessionModel",  "Models/sessionModel.py"),
]:
    try:
        _load_module(model_name, os.path.join(backend_dir, filename))
    except Exception as e:
        print(f"Warning: impossible de charger {model_name} : {e}")

# ─────────────────────────────────────────────────────────────
from sqlalchemy import create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smartcard.db')
engine = create_engine(DATABASE_URL, echo=False)

# Protection : --reset requis pour effacer les tables
if '--reset' in sys.argv:
    print("WARNING: suppression de toutes les tables...")
    confirm = input("Confirmer ? (oui/non) : ")
    if confirm.strip().lower() == 'oui':
        Base.metadata.drop_all(engine)
        print("Tables supprimées.")
    else:
        print("Annulé.")
        sys.exit(0)

print("Création des tables...")
Base.metadata.create_all(engine)
print("Base de données initialisée avec succès !")
print(f"   Fichier : {os.path.abspath('smartcard.db')}")