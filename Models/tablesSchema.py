"""
Ici le schema de la DB !
Architecture pour système de quiz/flashcards alimenté par IA

WORKFLOW:
1. User upload document → IA analyse → Détecte thème
2. Si thème nouveau → Génère questions → Stocke en DB
3. Si thème existant → Récupère questions existantes
4. User génère quiz (5/10/15 Q) ou flashcards (10/15/20 cartes)
5. Système pioche questions depuis DB

SÉCURITÉ:
- UUID partout (non-énumération)
- Soft delete
- Indexes stratégiques
- Validation MIME types
"""

from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey,
    Boolean, JSON, Index, UniqueConstraint, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# ****************************************************************************
# ENUMS
# ****************************************************************************

class QuestionType(enum.Enum):
    """Type de question"""
    QUIZ = 'quiz'           # QCM avec 4 choix
    FLASHCARD = 'flashcard' # Recto/verso

class Difficulty(enum.Enum):
    """Difficulté question"""
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

class SessionType(enum.Enum):
    """Type de session"""
    QUIZ = 'quiz'
    FLASHCARD = 'flashcard'


# ***************************************************************************
# TABLE 1 : USERS
# ****************************************************************************

class User(Base):
    __tablename__ = 'users'
    
    # Identité
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(255), unique=False, nullable=False)
    last_name = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    name = Column(String(100), nullable=False)
    
    # Vérification email
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    themes = relationship('Theme', back_populates='user', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_deleted', 'deleted_at'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


# ****************************************************************************
# TABLE 2 : THEMES (Catégories détectées par IA)
# ****************************************************************************

class Theme(Base):
    """
    Thèmes de contenu détectés automatiquement par l'IA
    """
    __tablename__ = 'themes'
    
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Données du thème
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Mots-clés pour matching IA (détection thème existant)
    # Exemple: ["algèbre", "équations", "polynômes", "factorisation"]
    keywords = Column(JSON, nullable=False, default=list)
    
    # Statistiques
    questions_count = Column(Integer, default=0)  # Nb questions dans ce thème
    times_used = Column(Integer, default=0)       # Popularité
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    user = relationship('User', back_populates='themes')
    questions = relationship('Question', back_populates='theme', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='theme')
    
    __table_args__ = (
        # Un user ne peut pas avoir 2 thèmes avec même nom
        UniqueConstraint('user_id', 'name', name='uq_user_theme_name'),
        Index('idx_themes_user', 'user_id')
    )
    
    def __repr__(self):
        return f"<Theme(id={self.id}, name={self.name}, questions={self.questions_count})>"


# ****************************************************************************
# TABLE 3 : QUESTIONS (Unifiée : quiz + flashcards)
# ****************************************************************************

class Question(Base):
    """
    Question unifiée (quiz OU flashcard)
    
    TYPE QUIZ:
    - question_text = "Ici c'est une question"
    - 4 answers (1 correcte, 3 fausses)
    
    TYPE FLASHCARD:
    - question_text = "Autre question" (RECTO)
    - 1 answer = "Paris" (VERSO)
    """
    __tablename__ = 'questions'
    
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    theme_id = Column(String(60), ForeignKey('themes.id', ondelete='CASCADE'), nullable=False)
    
    # Type et contenu
    type = Column(Enum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    difficulty = Column(Enum(Difficulty), default=Difficulty.MEDIUM)
    
    # Explication (affichée après réponse)
    explanation = Column(Text, nullable=True)
    
    # Métadata
    source = Column(String(50), default='ai_generated')  # 'ai_generated' ou 'user_created'
    
    # Statistiques d'utilisation
    times_used = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)  # Nb fois répondu correctement
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    theme = relationship('Theme', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_questions_theme', 'theme_id'),
        Index('idx_questions_type', 'type'),
        Index('idx_questions_difficulty', 'difficulty'),
    )
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type.value}, text={self.question_text[:50]}...)>"


# ============================================================================
# TABLE 4 : ANSWERS (Réponses aux questions)
# ============================================================================

class Answer(Base):
    """
    Réponses liées aux questions
    
    QUIZ: 4 answers (1 correcte, 3 fausses)
    FLASHCARD: 1 answer (la réponse du verso)
    """
    __tablename__ = 'answers'
    
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(60), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    
    # Contenu
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    
    # Ordre d'affichage (pour quiz)
    order_position = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    question = relationship('Question', back_populates='answers')
    
    __table_args__ = (
        Index('idx_answers_question', 'question_id'),
        Index('idx_answers_correct', 'is_correct'),
    )
    
    def __repr__(self):
        correct = "✓" if self.is_correct else "✗"
        return f"<Answer(id={self.id}, text={self.answer_text[:30]}..., correct={correct})>"


# ============================================================================
# TABLE 5 : SESSIONS (Historique quiz/flashcards)
# ============================================================================

class Session(Base):
    """
    Historique des quiz et flashcards passés
    
    Permet:
    - Statistiques utilisateur (taux de réussite, progression)
    - Éviter de reposer mêmes questions
    - Analytics (questions les plus difficiles)
    """
    __tablename__ = 'sessions'
    
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    theme_id = Column(String(60), ForeignKey('themes.id', ondelete='SET NULL'), nullable=True)
    
    # Type de session
    type = Column(Enum(SessionType), nullable=False)
    
    # Configuration
    questions_count = Column(Integer, nullable=False)  # 5/10/15 (quiz) ou 10/15/20 (flashcards)
    
    # Questions utilisées (IDs stockés en JSON)
    # Exemple: ["q1", "q5", "q12", "q20", "q35"]
    questions_ids = Column(JSON, nullable=False, default=list)
    
    # Résultats (pour quiz uniquement)
    score = Column(Integer, nullable=True)  # Points obtenus
    max_score = Column(Integer, nullable=True)  # Points maximum
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    user = relationship('User', back_populates='sessions')
    theme = relationship('Theme', back_populates='sessions')
    
    __table_args__ = (
        Index('idx_sessions_user', 'user_id'),
        Index('idx_sessions_theme', 'theme_id'),
        Index('idx_sessions_type', 'type'),
        Index('idx_sessions_completed', 'completed_at'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, type={self.type.value}, score={self.score}/{self.max_score})>"


# ============================================================================
# HELPERS - Méthodes utilitaires
# ============================================================================

def get_success_rate(question: Question) -> float:
    """Calcule le taux de réussite d'une question"""
    if question.times_used == 0:
        return 0.0
    return (question.times_correct / question.times_used) * 100


def get_user_stats(user_id: str, session) -> dict:
    """
    Statistiques complètes d'un utilisateur
    
    Returns:
        {
            'total_themes': int,
            'total_questions': int,
            'total_sessions': int,
            'quiz_sessions': int,
            'flashcard_sessions': int,
            'average_score': float,
            'favorite_theme': str
        }
    """
    from sqlalchemy import func
    
    # Total thèmes
    total_themes = session.query(Theme).filter(Theme.user_id == user_id).count()
    
    # Total questions (tous thèmes)
    total_questions = session.query(Question).join(Theme).filter(
        Theme.user_id == user_id
    ).count()
    
    # Sessions
    sessions_query = session.query(Session).filter(Session.user_id == user_id)
    total_sessions = sessions_query.count()
    quiz_sessions = sessions_query.filter(Session.type == SessionType.QUIZ).count()
    flashcard_sessions = sessions_query.filter(Session.type == SessionType.FLASHCARD).count()
    
    # Score moyen (quiz uniquement)
    avg_score = session.query(func.avg(Session.score)).filter(
        Session.user_id == user_id,
        Session.type == SessionType.QUIZ,
        Session.score.isnot(None)
    ).scalar() or 0.0

    return {
        'total_themes': total_themes,
        'total_questions': total_questions,
        'total_sessions': total_sessions,
        'quiz_sessions': quiz_sessions,
        'flashcard_sessions': flashcard_sessions,
        'average_score': round(avg_score, 2)
    }


# ============================================================================
# SCRIPT DE CRÉATION DES TABLES
# ============================================================================

if __name__ == '__main__':
    from sqlalchemy import create_engine
    import os
    
    # Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smartcard.db')
    
    # Créer engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # IMPORTANT: Supprime les anciennes tables si elles existent
    # ⚠️ EN PRODUCTION: Utiliser Alembic pour migrations !
    print("\n⚠️  Suppression des anciennes tables...")
    Base.metadata.drop_all(engine)
    
    # Créer nouvelles tables
    print("\n✅ Création des nouvelles tables...")
    Base.metadata.create_all(engine)
    
    print("\n✅ Tables créées avec succès!")
    print("\nTables créées :")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
