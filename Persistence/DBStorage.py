"""
Couche d'abstraction pour accès sécurisé à la base de données
Compatible avec le pattern HBNB

SÉCURITÉ :
- Requêtes préparées (protection injection SQL)
- Soft delete par défaut
- Gestion transactions
- Validation des entrées
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import Optional, List, Dict, Type, Any
from datetime import datetime
import os

# Import des modèles (Architecture HBNB)
from Models.tablesSchema import Base
from Models.userModel import User
from Models.themeModel import Theme
from Models.questionModel import Question
from Models.answerModel import Answer
from Models.sessionModel import Session


class DBStorage:
    """
    Gestionnaire de stockage base de données
    
    Pattern Repository : interface unifiée pour toutes les opérations DB
    Architecture HBNB (Holberton School)
    """
    
    __engine = None
    __session = None
    
    # Classes disponibles
    classes = {
        'User': User,
        'Theme': Theme,
        'Question': Question,
        'Answer': Answer,
        'Session': Session
    }
    
    def __init__(self):
        """Initialise la connexion à la base de données"""
        database_url = os.getenv('DATABASE_URL', 'sqlite:///smartcard.db')
        
        # Configuration selon le type de DB
        if database_url.startswith('sqlite'):
            # SQLite : check_same_thread=False pour Flask
            self.__engine = create_engine(
                database_url,
                echo=False,  # True en dev pour voir les requêtes SQL
                connect_args={'check_same_thread': False}
            )
        else:
            # PostgreSQL/MySQL
            self.__engine = create_engine(
                database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True  # Vérifie connexion avant utilisation
            )
        
        # Session factory thread-safe
        session_factory = sessionmaker(
            bind=self.__engine,
            expire_on_commit=False
        )
        self.__session = scoped_session(session_factory)
    
    def all(self, cls: Type[Base] = None, include_deleted: bool = False) -> Dict[str, Any]:
        """
        Récupère tous les objets d'une classe
        
        Args:
            cls: Classe à récupérer (User, Document...) ou None pour toutes
            include_deleted: Inclure objets soft-deleted
            
        Returns:
            Dict {ClassName.id: object}
            
        Exemple:
            storage.all(User)  # Tous les users actifs
        """
        objects = {}
        
        if cls:
            classes_to_query = [cls]
        else:
            classes_to_query = self.classes.values()
        
        for class_type in classes_to_query:
            query = self.__session.query(class_type)
            
            # Filtre soft delete
            if not include_deleted and hasattr(class_type, 'deleted_at'):
                query = query.filter(class_type.deleted_at.is_(None))
            
            for obj in query.all():
                key = f"{obj.__class__.__name__}.{obj.id}"
                objects[key] = obj
        
        return objects
    
    def new(self, obj: Base):
        """
        Ajoute un nouvel objet à la session
        
        Args:
            obj: Instance de modèle à ajouter
        """
        self.__session.add(obj)
    
    def save(self):
        """
        Commit les changements dans la base de données
        
        SÉCURITÉ : Gestion automatique des transactions
        """
        try:
            self.__session.commit()
        except Exception as e:
            self.__session.rollback()
            raise e
    
    def delete(self, obj: Base = None, hard_delete: bool = False):
        """
        Supprime un objet (soft delete par défaut)
        
        Args:
            obj: Objet à supprimer
            hard_delete: True = suppression réelle, False = soft delete
            
        SÉCURITÉ : Soft delete conserve les données pour audit
        """
        if obj is None:
            return
        
        if hard_delete:
            # Suppression réelle
            self.__session.delete(obj)
        else:
            # Soft delete
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.utcnow()
                self.__session.add(obj)
    
    def reload(self):
        """Recharge la session depuis la base de données"""
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(
            sessionmaker(bind=self.__engine, expire_on_commit=False)
        )
    
    def close(self):
        """Ferme la session"""
        self.__session.remove()
    
    # ********************************************************
    # MÉTHODES DE RECHERCHE SÉCURISÉES
    # ********************************************************
    
    def get(self, cls: Type[Base], id: str, include_deleted: bool = False) -> Optional[Base]:
        """
        Récupère un objet par son ID
        
        Args:
            cls: Classe du modèle
            id: ID de l'objet
            include_deleted: Inclure objets supprimés
            
        Returns:
            Objet ou None
        """
        if not cls or not id:
            return None
        
        query = self.__session.query(cls).filter(cls.id == id)
        
        if not include_deleted and hasattr(cls, 'deleted_at'):
            query = query.filter(cls.deleted_at.is_(None))
        
        return query.first()
    
    def get_by_email(self, cls: Type[Base], email: str, include_deleted: bool = False) -> Optional[Base]:
        """
        Récupère un objet par email (User principalement)
        
        SÉCURITÉ : Requête préparée (protection injection SQL)
        """
        if not cls or not email:
            return None
        
        if not hasattr(cls, 'email'):
            return None
        
        # Normalisation email
        email = email.strip().lower()
        
        query = self.__session.query(cls).filter(cls.email == email)
        
        if not include_deleted and hasattr(cls, 'deleted_at'):
            query = query.filter(cls.deleted_at.is_(None))
        
        return query.first()
    
    def filter_by(self, cls: Type[Base], include_deleted: bool = False, **filters) -> List[Base]:
        """
        Filtre les objets selon critères
        
        Args:
            cls: Classe du modèle
            include_deleted: Inclure soft-deleted
            **filters: Critères de filtrage (user_id=123, theme_id=456...)
            
        Returns:
            Liste d'objets
            
        Exemple:
            storage.filter_by(Flashcard, user_id='abc', theme_id='xyz')
        """
        query = self.__session.query(cls)
        
        # Applique les filtres
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        # Filtre soft delete
        if not include_deleted and hasattr(cls, 'deleted_at'):
            query = query.filter(cls.deleted_at.is_(None))
        
        return query.all()
    
    def count(self, cls: Type[Base], include_deleted: bool = False, **filters) -> int:
        """
        Compte les objets selon critères
        
        Exemple:
            storage.count(User)  # Nombre total users
            storage.count(Flashcard, theme_id='abc')  # Flashcards d'un thème
        """
        query = self.__session.query(cls)
        
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        if not include_deleted and hasattr(cls, 'deleted_at'):
            query = query.filter(cls.deleted_at.is_(None))
        
        return query.count()
    
    # ********************************************************
    # MÉTHODES SPÉCIFIQUES MÉTIER
    # ********************************************************
    
    def get_user_themes(self, user_id: str) -> List[Theme]:
        """Récupère tous les thèmes d'un utilisateur"""
        return self.filter_by(Theme, user_id=user_id)
    
    def get_theme_flashcards(self, theme_id: str) -> List[Flashcard]:
        """Récupère toutes les flashcards d'un thème"""
        return self.filter_by(Flashcard, theme_id=theme_id)
    
    def get_flashcards_to_review(self, user_id: str, limit: int = 20) -> List[Flashcard]:
        """
        Récupère les flashcards à réviser (spaced repetition)
        
        Args:
            user_id: ID utilisateur
            limit: Nombre max de cards
        """
        now = datetime.utcnow()
        
        # Flashcards où next_review_at <= maintenant
        query = self.__session.query(Flashcard).join(Document).filter(
            and_(
                Document.user_id == user_id,
                Flashcard.deleted_at.is_(None),
                Flashcard.next_review_at <= now
            )
        ).order_by(Flashcard.next_review_at).limit(limit)
        
        return query.all()
    
    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """
        Statistiques utilisateur
        
        Returns:
            {
                'total_themes': int,
                'total_flashcards': int,
                'total_quizzes': int,
                'flashcards_reviewed': int
            }
        """
        return {
            'total_themes': self.count(Theme, user_id=user_id),
            'total_documents': self.count(Document, user_id=user_id),
            'total_quizzes': self.count(Quiz, user_id=user_id),
            'total_flashcards': self.__session.query(Flashcard).join(Document).filter(
                Document.user_id == user_id
            ).count()
        }
    
    # ********************************************************
    # CONTEXT MANAGER POUR TRANSACTIONS
    # ********************************************************
    
    @contextmanager
    def transaction(self):
        """
        Context manager pour transactions sécurisées
        
        Usage:
            with storage.transaction():
                user = User(email='test@test.com')
                storage.new(user)
                storage.save()
                # Auto-rollback si erreur
        """
        try:
            yield self.__session
            self.__session.commit()
        except Exception as e:
            self.__session.rollback()
            raise e
        finally:
            self.__session.close()


# ********************************************************
# INSTANCE GLOBALE (Pattern Singleton)
# ********************************************************

storage = DBStorage()