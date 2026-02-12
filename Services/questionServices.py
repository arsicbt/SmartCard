"""
Quiz Service - Logique métier pour les quiz et flashcards

Gère :
- Création de questions et réponses
- Génération de sessions de quiz/flashcards
- Calcul des scores et statistiques
"""

from Models.questionModel import Question
from Models.answerModel import Answer
from Models.sessionModel import Session
from Models.themeModel import Theme
from Models.tablesSchema import QuestionType, Difficulty, SessionType
from typing import Optional, List, Dict, Tuple
import random


class QuizzService:
    """
    Service de gestion des quiz et flashcards
    
    Logique métier PURE (pas de dépendances HTTP)
    """
    
    def __init__(self, storage):
        """
        Args:
            storage: Instance de DBStorage
        """
        self.storage = storage
    
    # ********************************************************
    # CREATION QUESTIONS
    # ********************************************************
    
    def create_question(
        self,
        theme_id: str,
        question_text: str,
        question_type: str = 'quiz',
        difficulty: str = 'medium'
    ) -> Tuple[Optional[Question], Optional[str]]:
        """
        Crée une nouvelle question
        
        Args:
            theme_id: ID du thème
            question_text: Texte de la question
            question_type: 'quiz' ou 'flashcard'
            difficulty: 'easy', 'medium' ou 'hard'
        
        Returns:
            Tuple (Question créée, message d'erreur)
        """
        # Vérifier que le thème existe
        theme = self.storage.get('Theme', theme_id)
        if not theme:
            return None, "Thème non trouvé"
        
        # Valider le type
        try:
            q_type = QuestionType.QUIZ if question_type.lower() == 'quiz' else QuestionType.FLASHCARD
        except:
            return None, "Type de question invalide (quiz ou flashcard)"
        
        # Valider la difficulté
        try:
            diff = Difficulty[difficulty.upper()]
        except:
            return None, "Difficulté invalide (easy, medium ou hard)"
        
        # Créer la question
        question = Question(
            theme_id=theme_id,
            type=q_type,
            question_text=question_text.strip(),
            difficulty=diff
        )
        
        self.storage.new(question)
        self.storage.save()
        
        # Incrémenter le compteur du thème
        theme.questions_count += 1
        self.storage.save()
        
        return question, None
    
    def add_answer_to_question(
        self,
        question_id: str,
        answer_text: str,
        is_correct: bool = False
    ) -> Tuple[Optional[Answer], Optional[str]]:
        """
        Ajoute une réponse à une question
        
        Args:
            question_id: ID de la question
            answer_text: Texte de la réponse
            is_correct: Réponse correcte ou non
        
        Returns:
            Tuple (Answer créée, message d'erreur)
        """
        # Vérifier que la question existe
        question = self.storage.get('Question', question_id)
        if not question:
            return None, "Question non trouvée"
        
        # Créer la réponse
        answer = Answer(
            question_id=question_id,
            answer_text=answer_text.strip(),
            is_correct=is_correct
        )
        
        self.storage.new(answer)
        self.storage.save()
        
        return answer, None
    
    # ********************************************************
    # SESSIONS DE QUIZ
    # ********************************************************
    
    def create_quiz_session(
        self,
        user_id: str,
        theme_id: str,
        questions_count: int = 10
    ) -> Tuple[Optional[Session], List[Question], Optional[str]]:
        """
        Crée une session de quiz
        
        Sélectionne aléatoirement des questions du thème.
        
        Args:
            user_id: ID de l'utilisateur
            theme_id: ID du thème
            questions_count: Nombre de questions (5, 10 ou 15)
        
        Returns:
            Tuple (Session créée, Liste des questions, message d'erreur)
        """
        # Vérifier que le thème existe
        theme = self.storage.get('Theme', theme_id)
        if not theme:
            return None, [], "Thème non trouvé"
        
        # Récupérer les questions du thème (type QUIZ uniquement)
        all_questions = self.storage.filter_by('Question', theme_id=theme_id)
        quiz_questions = [q for q in all_questions if q.type == QuestionType.QUIZ and not q.is_deleted()]
        
        if len(quiz_questions) < questions_count:
            return None, [], f"Pas assez de questions (minimum {questions_count} requis)"
        
        # Sélectionner aléatoirement
        selected_questions = random.sample(quiz_questions, questions_count)
        question_ids = [q.id for q in selected_questions]
        
        # Créer la session
        session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=SessionType.QUIZ,
            questions_count=questions_count,
            questions_ids=question_ids
        )
        
        self.storage.new(session)
        self.storage.save()
        
        # Incrémenter le compteur du thème
        theme.increment_usage()
        self.storage.save()
        
        return session, selected_questions, None
    
    def create_flashcard_session(
        self,
        user_id: str,
        theme_id: str,
        cards_count: int = 15
    ) -> Tuple[Optional[Session], List[Question], Optional[str]]:
        """
        Crée une session de flashcards
        
        Args:
            user_id: ID de l'utilisateur
            theme_id: ID du thème
            cards_count: Nombre de cartes (10, 15 ou 20)
        
        Returns:
            Tuple (Session créée, Liste des flashcards, message d'erreur)
        """
        # Vérifier que le thème existe
        theme = self.storage.get('Theme', theme_id)
        if not theme:
            return None, [], "Thème non trouvé"
        
        # Récupérer les flashcards du thème
        all_questions = self.storage.filter_by('Question', theme_id=theme_id)
        flashcards = [q for q in all_questions if q.type == QuestionType.FLASHCARD and not q.is_deleted()]
        
        if len(flashcards) < cards_count:
            return None, [], f"Pas assez de flashcards (minimum {cards_count} requis)"
        
        # Sélectionner aléatoirement
        selected_cards = random.sample(flashcards, cards_count)
        card_ids = [c.id for c in selected_cards]
        
        # Créer la session
        session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=SessionType.FLASHCARD,
            questions_count=cards_count,
            questions_ids=card_ids
        )
        
        self.storage.new(session)
        self.storage.save()
        
        # Incrémenter le compteur du thème
        theme.increment_usage()
        self.storage.save()
        
        return session, selected_cards, None
    
    # ********************************************************
    # SOUMISSION QUIZ
    # ********************************************************
    
    def submit_quiz(
        self,
        session_id: str,
        answers: Dict[str, str]  # {question_id: answer_id}
    ) -> Tuple[Optional[Session], Optional[Dict], Optional[str]]:
        """
        Soumet un quiz terminé et calcule le score
        
        Args:
            session_id: ID de la session
            answers: Dictionnaire {question_id: answer_id}
        
        Returns:
            Tuple (Session mise à jour, Résultats détaillés, message d'erreur)
        """
        # Récupérer la session
        session = self.storage.get('Session', session_id)
        if not session:
            return None, None, "Session non trouvée"
        
        if session.is_completed():
            return None, None, "Session déjà terminée"
        
        if session.type != SessionType.QUIZ:
            return None, None, "Cette session n'est pas un quiz"
        
        # Calculer le score
        score = 0
        max_score = len(session.questions_ids)
        results = []
        
        for question_id in session.questions_ids:
            question = self.storage.get('Question', question_id)
            if not question:
                continue
            
            # Récupérer les réponses de la question
            question_answers = self.storage.filter_by('Answer', question_id=question_id)
            correct_answer = next((a for a in question_answers if a.is_correct), None)
            
            # Vérifier si l'utilisateur a répondu correctement
            user_answer_id = answers.get(question_id)
            is_correct = user_answer_id == correct_answer.id if correct_answer else False
            
            if is_correct:
                score += 1
            
            # Incrémenter les stats de la question
            question.increment_usage(is_correct=is_correct)
            
            results.append({
                'question_id': question_id,
                'user_answer_id': user_answer_id,
                'correct_answer_id': correct_answer.id if correct_answer else None,
                'is_correct': is_correct
            })
        
        # Compléter la session
        session.complete_session(score=score, max_score=max_score)
        self.storage.save()
        
        return session, {
            'score': score,
            'max_score': max_score,
            'success_rate': session.get_success_rate(),
            'details': results
        }, None
    
    # ********************************************************
    # STATISTIQUES
    # ********************************************************
    
    def get_user_stats(self, user_id: str) -> Dict:
        """
        Récupère les statistiques d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Dictionnaire de statistiques
        """
        # Récupérer toutes les sessions de l'utilisateur
        all_sessions = self.storage.filter_by('Session', user_id=user_id)
        completed_sessions = [s for s in all_sessions if s.is_completed()]
        
        quiz_sessions = [s for s in completed_sessions if s.type == SessionType.QUIZ]
        flashcard_sessions = [s for s in completed_sessions if s.type == SessionType.FLASHCARD]
        
        # Calculer la moyenne des scores
        avg_score = 0.0
        if quiz_sessions:
            total_success = sum(s.get_success_rate() for s in quiz_sessions)
            avg_score = total_success / len(quiz_sessions)
        
        return {
            'total_sessions': len(completed_sessions),
            'quiz_sessions': len(quiz_sessions),
            'flashcard_sessions': len(flashcard_sessions),
            'average_score': round(avg_score, 2)
        }
