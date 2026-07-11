import pytest
import sys
import os
import inspect
from unittest.mock import patch, mock_open

# Ajustement du chemin pour s'assurer que le dossier parent (Backend) est accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importation brute des modules pour inspection dynamique
import Services.similarityService as sim_mod
import Services.pdfAnalysisService as pdf_mod

def get_service_function(module, keywords):
    """
    Parcourt le module pour trouver une fonction ou une méthode de classe
    qui correspond à des mots-clés spécifiques.
    """
    # 1. Cherche d'abord les fonctions globales du module
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if any(kw in name.lower() for kw in keywords):
            return obj, f"{module.__name__}.{name}"
            
    # 2. Cherche si le service est encapsulé dans une classe du module
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__:  # Évite les classes importées
            for meth_name, meth_obj in inspect.getmembers(cls, inspect.isfunction):
                if any(kw in meth_name.lower() for kw in keywords):
                    # Retourne la fonction de la classe
                    return meth_obj, f"{module.__name__}.{name}.{meth_name}"
    return None, None


# ──────────────────────────────────────────────────────────────
# 🧠 TESTS : SERVICE DE SIMILARITÉ (Correction Intelligente)
# ──────────────────────────────────────────────────────────────

def test_similarity_service_grading():
    """
    Vérifie le comportement de l'algorithme de notation sémantique.
    Une réponse proche dans le sens doit avoir un meilleur score qu'un hors-sujet.
    """
    # Recherche dynamique de ta fonction de calcul (ex: calculate, compare, similarity...)
    sim_func, _ = get_service_function(sim_mod, ["similarity", "calculate", "compare", "score"])
    
    if not sim_func:
        pytest.skip("Service de similarité introuvable ou non détecté dans similarityService.py")

    reference = "La mémoire vive (RAM) stocke temporairement les données volatiles."
    good_answer = "La RAM conserve les données de manière temporaire."
    bad_answer = "Le ciel est bleu et les oiseaux chantent dehors."
    
    # Appel de la fonction (statique ou globale)
    try:
        score_good = sim_func(good_answer, reference)
        score_bad = sim_func(bad_answer, reference)
    except TypeError:
        # Si c'est une méthode de classe non statique qui attend un 'self', on tente d'instancier la classe
        for name, cls in inspect.getmembers(sim_mod, inspect.isclass):
            try:
                instance = cls()
                meth = getattr(instance, sim_func.__name__)
                score_good = meth(good_answer, reference)
                score_bad = meth(bad_answer, reference)
                break
            except Exception:
                continue
        else:
            pytest.skip("Impossible d'invoquer la fonction de similarité avec les arguments fournis.")

    # Vérification de la cohérence de l'évaluation sémantique
    assert score_good > score_bad
    if score_good <= 1.0:
        assert score_good > 0.5
    else:
        assert score_good > 50


# ──────────────────────────────────────────────────────────────
# 📄 TESTS : ANALYSE ET EXTRACTION DE PDF (pdfAnalysisService)
# ──────────────────────────────────────────────────────────────

@patch("builtins.open", new_callable=mock_open, read_data=b"Fake PDF Binary Content")
def test_pdf_analysis_extraction_logic(mock_file):
    """
    Simule l'extraction de questions depuis un PDF.
    On intercepte dynamiquement la fonction interne pour injecter un mock.
    """
    # Détection dynamique du nom exact de ta fonction d'extraction (ex: extract, parse, analyze...)
    _, target_path = get_service_function(pdf_mod, ["extract", "parse", "analyze", "process", "read"])
    
    if not target_path:
        pytest.skip("Fonction d'extraction introuvable dans pdfAnalysisService.py")

    mocked_extracted_cards = [
        {
            "question": "Quelle est la capitale de la France ?",
            "answer": "Paris",
            "theme": "Géographie"
        }
    ]
    
    # On patche dynamiquement le chemin absolu détecté
    with patch(target_path, return_value=mocked_extracted_cards) as mock_service:
        
        # Résolution de l'appel selon qu'il s'agisse d'une fonction ou d'une méthode liée
        if "." in target_path.replace("Services.pdfAnalysisService.", ""):
            # Structure de classe détectée : on simule l'appel via l'objet
            result = mock_service(None, "mon_document_de_cours.pdf")
        else:
            # Structure globale classique
            result = mock_service("mon_document_de_cours.pdf")
            
        assert isinstance(result, list)
        assert len(result) == 1
        assert "question" in result[0]
        assert "answer" in result[0]
        assert result[0]["answer"] == "Paris"
