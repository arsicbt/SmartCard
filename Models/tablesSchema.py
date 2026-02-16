"""
Table Schema - Base SQLAlchemy et Enums

Contient UNIQUEMENT :
- Base : Classe de base SQLAlchemy
- Enums : Types énumérés pour QuestionType, Difficulty, SessionType

Les modèles (User, Theme, etc.) sont dans des fichiers séparés
et héritent de BaseModel qui hérite lui-même de Base.
"""

from sqlalchemy.ext.declarative import declarative_base
import enum

# ****************************************************************************
# BASE SQLALCHEMY
# ****************************************************************************
Base = declarative_base()


# ****************************************************************************
# ENUMS
# ****************************************************************************
class QuestionType(enum.Enum):
    """
    Type de question
    
    - QUIZ : QCM avec choix multiples
    - FLASHCARD : Carte recto/verso
    """
    QUIZ = 'quiz'
    FLASHCARD = 'flashcard'


class Difficulty(enum.Enum):
    """
    Niveau de difficulté d'une question
    
    - EASY : Facile
    - MEDIUM : Moyen
    - HARD : Difficile
    """
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


class SessionType(enum.Enum):
    """
    Type de session d'étude
    
    - QUIZ : Session de quiz
    - FLASHCARD : Session de révision flashcards
    """
    QUIZ = 'quiz'
    FLASHCARD = 'flashcard'
