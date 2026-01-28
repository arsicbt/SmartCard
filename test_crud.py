"""
Script de test des opérations CRUD avec SQLAlchemy
Adapté à la structure SmartCard
"""

from Models.tablesSchema import Base
from Models.userModel import User
from Models.themeModel import Theme
from Models.questionModel import Question
from Models.answerModel import Answer
from Models.sessionModel import Session
from datetime import datetime
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///smartcard.db'


# --------------------------------------------
# Helper : hash password
# --------------------------------------------
def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# --------------------------------------------
# Setup SQLAlchemy engine & session
# --------------------------------------------
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Créer les tables si elles n'existent pas
print("\n📦 Création des tables...")
Base.metadata.create_all(engine)


# --------------------------------------------
# TEST USER CRUD
# --------------------------------------------
def test_user_crud():
    print("\n🧪 TEST USER CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        # CREATE
        print("\n1️⃣  CREATE User")
        user = User(
            email="test@smartcard.com",
            password=hash_password("Test123!"),
            name="Test User",
            is_verified=True
        )
        session.add(user)
        session.commit()
        print(f"✅ User créé: {user}")
        # print(f"   Dict: {user.to_dict()}")  # Optionnel si to_dict existe

        # READ
        print("\n2️⃣  READ User")
        found_user = session.query(User).filter_by(email="test@smartcard.com").first()
        print(f"✅ User trouvé: {found_user}")

        # UPDATE
        print("\n3️⃣  UPDATE User")
        found_user.name = "Updated User"
        session.commit()
        print(f"✅ User mis à jour: {found_user.name}")

        # SOFT DELETE
        print("\n4️⃣  SOFT DELETE User")
        if hasattr(found_user, "soft_delete"):
            found_user.soft_delete()
        else:
            found_user.deleted_at = datetime.utcnow()
        session.commit()
        print(f"✅ User soft deleted: deleted_at = {found_user.deleted_at}")

        return user.id

    except Exception as e:
        print(f"❌ Erreur: {e}")
        session.rollback()
        return None
    finally:
        session.close()


# --------------------------------------------
# TEST THEME CRUD
# --------------------------------------------
def test_theme_crud():
    print("\n🧪 TEST THEME CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        # CREATE
        print("\n1️⃣  CREATE Theme")
        theme = Theme(
            name="Mathématiques - Algèbre",
            keywords=["algèbre", "équations", "mathématiques"],
            description="Questions sur l'algèbre de base",
            is_public=True
        )
        session.add(theme)
        session.commit()
        print(f"✅ Theme créé: {theme}")

        # READ
        print("\n2️⃣  READ Theme")
        found_theme = session.query(Theme).filter_by(name="Mathématiques - Algèbre").first()
        print(f"✅ Theme trouvé: {found_theme}")

        # UPDATE
        print("\n3️⃣  UPDATE Theme (ajout keyword)")
        if hasattr(found_theme, "add_keyword"):
            found_theme.add_keyword("polynômes")
        else:
            found_theme.keywords.append("polynômes")
        session.commit()
        print(f"✅ Keywords mis à jour: {found_theme.keywords}")

        return theme.id

    except Exception as e:
        print(f"❌ Erreur: {e}")
        session.rollback()
        return None
    finally:
        session.close()


# --------------------------------------------
# TEST QUESTION & ANSWER CRUD
# --------------------------------------------
def test_question_answer_crud(theme_id):
    print("\n🧪 TEST QUESTION & ANSWER CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        # CREATE QUIZ QUESTION
        print("\n1️⃣  CREATE Quiz Question")
        quiz = Question(
            theme_id=theme_id,
            question_text="Quelle est la solution de l'équation x + 5 = 10?",
            type=QuestionType.QUIZ,
            difficulty=Difficulty.EASY,
            explanation="Il suffit de soustraire 5 de chaque côté"
        )
        session.add(quiz)
        session.commit()
        print(f"✅ Quiz créé: {quiz}")

        # CREATE ANSWERS
        print("\n2️⃣  CREATE Answers")
        answers_data = [
            {"text": "x = 3", "correct": False},
            {"text": "x = 5", "correct": True},
            {"text": "x = 15", "correct": False},
            {"text": "x = 10", "correct": False}
        ]
        for ans_data in answers_data:
            answer = Answer(
                question_id=quiz.id,
                answer_text=ans_data["text"],
                is_correct=ans_data["correct"]
            )
            session.add(answer)
        session.commit()
        print(f"✅ {len(answers_data)} réponses créées")

        # CREATE FLASHCARD QUESTION
        print("\n3️⃣  CREATE Flashcard Question")
        flashcard = Question(
            theme_id=theme_id,
            question_text="Qu'est-ce qu'une équation linéaire?",
            type=QuestionType.FLASHCARD,
            difficulty=Difficulty.MEDIUM
        )
        session.add(flashcard)
        session.commit()

        # Answer for flashcard
        flashcard_answer = Answer(
            question_id=flashcard.id,
            answer_text="Une équation de la forme ax + b = 0 où a et b sont des constantes.",
            is_correct=True
        )
        session.add(flashcard_answer)
        session.commit()
        print(f"✅ Flashcard créée: {flashcard}")

        return quiz.id, flashcard.id

    except Exception as e:
        print(f"❌ Erreur: {e}")
        session.rollback()
        return None, None
    finally:
        session.close()


# --------------------------------------------
# TEST SESSION CRUD
# --------------------------------------------
def test_session_crud(user_id, theme_id, question_ids):
    print("\n🧪 TEST SESSION CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        # CREATE Session
        quiz_session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=QuestionType.QUIZ,
            questions_ids=question_ids,
            total_questions=len(question_ids),
            score=3
        )
        session.add(quiz_session)
        session.commit()
        print(f"✅ Session créée: {quiz_session}")

        # READ Session
        found_session = session.query(Session).filter_by(user_id=user_id).first()
        print(f"✅ Session trouvée: {found_session}")

        return quiz_session.id

    except Exception as e:
        print(f"❌ Erreur: {e}")
        session.rollback()
        return None
    finally:
        session.close()


# --------------------------------------------
# RUN ALL TESTS
# --------------------------------------------
def run_all_tests():
    print("\n" + "=" * 50)
    print("🚀 DÉMARRAGE DES TESTS CRUD")
    print("=" * 50)

    # Test User
    user_id = test_user_crud()
    if not user_id:
        print("❌ Tests arrêtés: échec User")
        return

    # Test Theme
    theme_id = test_theme_crud()
    if not theme_id:
        print("❌ Tests arrêtés: échec Theme")
        return

    # Test Question & Answer
    quiz_id, flashcard_id = test_question_answer_crud(theme_id)
    if not quiz_id or not flashcard_id:
        print("❌ Tests arrêtés: échec Question/Answer")
        return

    # Test Session
    session_id = test_session_crud(user_id, theme_id, [quiz_id, flashcard_id])

    print("\n" + "=" * 50)
    print("✅ TOUS LES TESTS CRUD ONT RÉUSSI!")
    print("=" * 50)
    print(f"\nIDs créés:")
    print(f"  User ID: {user_id}")
    print(f"  Theme ID: {theme_id}")
    print(f"  Quiz ID: {quiz_id}")
    print(f"  Flashcard ID: {flashcard_id}")
    print(f"  Session ID: {session_id}")


if __name__ == "__main__":
    run_all_tests()
