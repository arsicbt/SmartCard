"""
Fichier de tests CRUD complets pour le projet SmartCard
Version cohérente avec les règles métier :
- User actif requis pour créer Theme / Question / Session
- Soft delete testé séparément
"""

from Models.tablesSchema import (
    Base, User, Theme, Question, Answer, Session,
    QuestionType, Difficulty, SessionType
)

from Utils.passwordSecurity import PasswordManager
from datetime import datetime, UTC
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///smartcard.db"


# --------------------------------------------
# Setup SQLAlchemy
# --------------------------------------------
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

print("\n📦 Création des tables...")
Base.metadata.create_all(engine)


# --------------------------------------------
# TEST USER CRUD (sans soft delete)
# --------------------------------------------
def test_user_crud():
    print("\n🧪 TEST USER CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        print("\n1️⃣ CREATE User")
        user = User(
            first_name="Arsinoé",
            last_name="Chobert",
            email="test@smartcard.com",
            password=PasswordManager.hash_password("Test123!")
            name="Test User",
            is_verified=True
        )
        session.add(user)
        session.commit()
        print(f"✅ User créé: {user}")

        print("\n2️⃣ READ User")
        found_user = session.query(User).filter_by(email="test@smartcard.com").first()
        print(f"✅ User trouvé: {found_user}")

        print("\n3️⃣ UPDATE User")
        found_user.name = "Updated User"
        session.commit()
        print(f"✅ User mis à jour: {found_user.name}")

        return user.id

    except Exception as e:
        print(f"❌ Erreur User CRUD: {e}")
        session.rollback()
        return None
    finally:
        session.close()


# --------------------------------------------
# TEST THEME CRUD
# --------------------------------------------
def test_theme_crud(user_id):
    print("\n🧪 TEST THEME CRUD")
    print("=" * 50)
    session = SessionLocal()

    try:
        print("\n1️⃣ CREATE Theme")
        theme = Theme(
            user_id=user_id,
            name="Mathématiques - Algèbre",
            description="Questions sur l'algèbre de base",
            keywords=["algèbre", "équations", "mathématiques"],
        )
        session.add(theme)
        session.commit()
        print(f"✅ Theme créé: {theme}")

        print("\n2️⃣ READ Theme")
        found_theme = session.query(Theme).filter_by(name=theme.name).first()
        print(f"✅ Theme trouvé: {found_theme}")

        print("\n3️⃣ UPDATE Theme")
        found_theme.keywords.append("polynômes")
        session.commit()
        print(f"✅ Keywords mis à jour: {found_theme.keywords}")

        return theme.id

    except Exception as e:
        print(f"❌ Erreur Theme CRUD: {e}")
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
        print("\n1️⃣ CREATE quizz Question")
        quizz = Question(
            question_ids=question_ids,
            theme_id=theme_id,
            question_text="Quelle est la solution de x + 5 = 10 ?",
            type="QUIZZ",
            difficulty=Difficulty.EASY,
            questions_count=len(question_ids),
            explanation="Soustraire 5 des deux côtés"
        )
        session.add(quizz)
        session.commit()
        print(f"✅ quizz créé: {quizz}")

        print("\n2️⃣ CREATE Answers")
        answers = [
            ("x = 3", False),
            ("x = 5", True),
            ("x = 15", False),
            ("x = 10", False),
        ]
        for text, correct in answers:
            session.add(Answer(
                question_id=quizz.id,
                answer_text=text,
                is_correct=correct
            ))
        session.commit()
        print("✅ Réponses créées")

        print("\n3️⃣ CREATE Flashcard Question")
        flashcard = Question(
            question_ids=question_ids,
            theme_id=theme_id,
            question_text="Qu'est-ce qu'une équation linéaire ?",
            type=QuestionType.FLASHCARD,
            questions_count=len(question_ids),
            difficulty=Difficulty.MEDIUM
        )
        session.add(flashcard)
        session.commit()

        session.add(Answer(
            question_id=flashcard.id,
            answer_text="Une équation de la forme ax + b = 0",
            is_correct=True
        ))
        session.commit()
        print(f"✅ Flashcard créée: {flashcard}")

        return quizz.id, flashcard.id

    except Exception as e:
        print(f"❌ Erreur Question/Answer CRUD: {e}")
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
        quizz_session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type="QUIZZ",
            questions_ids=question_ids,
            score=3
        )
        session.add(quizz_session)
        session.commit()
        print(f"✅ Session créée: {quizz_session}")

        return quizz_session.id

    except Exception as e:
        print(f"❌ Erreur Session CRUD: {e}")
        session.rollback()
        return None
    finally:
        session.close()


# --------------------------------------------
# TEST USER SOFT DELETE (séparé)
# --------------------------------------------
def test_user_soft_delete(user_id):
    print("\n🧪 TEST USER SOFT DELETE")
    print("=" * 50)
    session = SessionLocal()

    try:
        user = session.get(User, user_id)
        user.deleted_at = datetime.now(UTC)
        session.commit()
        print(f"✅ User soft deleted à {user.deleted_at}")
    finally:
        session.close()


# --------------------------------------------
# RUN ALL TESTS
# --------------------------------------------
def run_all_tests():
    print("\n" + "=" * 50)
    print("🚀 DÉMARRAGE DES TESTS CRUD")
    print("=" * 50)

    user_id = test_user_crud()
    if not user_id:
        return

    theme_id = test_theme_crud(user_id)
    if not theme_id:
        return

    quizz_id, flashcard_id = test_question_answer_crud(theme_id)
    if not quizz_id:
        return

    test_session_crud(user_id, theme_id, [quizz_id, flashcard_id])
    test_user_soft_delete(user_id)

    print("\n" + "=" * 50)
    print("✅ TOUS LES TESTS CRUD ONT RÉUSSI")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
