"""
Test CRUD - SmartCard
Architecture HBNB (Holberton School)

Tests complets pour tous les modèles :
- User
- Theme
- Question
- Answer
- Session
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.tablesSchema import Base, QuestionType, Difficulty, SessionType
from Models.userModel import User
from Models.themeModel import Theme
from Models.questionModel import Question
from Models.answerModel import Answer
from Models.sessionModel import Session
from Utils.passwordSecurity import PasswordManager

# Configuration
DATABASE_URL = 'sqlite:///smartcard_test.db'
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Créer les tables
print("\n" + "=" * 60)
print("📦 CRÉATION DES TABLES")
print("=" * 60)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("✅ Tables créées\n")


# ============================================================================
# TEST 1 : USER CRUD
# ============================================================================
def test_user_crud():
    """Test CRUD User"""
    print("=" * 60)
    print("🧪 TEST USER CRUD")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # CREATE
        print("\n1️⃣  CREATE User")
        user, error = User.validate_and_create(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="SecurePass123!",
            name="JohnD"
        )
        
        if error:
            print(f"❌ Erreur : {error}")
            return None
        
        session.add(user)
        session.commit()
        print(f"✅ User créé : {user.email}")
        
        # READ
        print("\n2️⃣  READ User")
        found = session.query(User).filter_by(email="john.doe@test.com").first()
        print(f"✅ User trouvé : {found.first_name} {found.last_name}")
        
        # UPDATE
        print("\n3️⃣  UPDATE User")
        found.first_name = "Johnny"
        found.update_timestamp()
        session.commit()
        print(f"✅ User mis à jour : {found.first_name}")
        
        # VERIFY PASSWORD
        print("\n4️⃣  VERIFY Password")
        valid = found.verify_password("SecurePass123!")
        print(f"✅ Password valide : {valid}")
        
        # SOFT DELETE
        print("\n5️⃣  SOFT DELETE")
        found.soft_delete()
        session.commit()
        print(f"✅ User soft deleted : {found.is_deleted()}")
        
        return user.id
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        session.rollback()
        return None
    finally:
        session.close()


# ============================================================================
# TEST 2 : THEME CRUD
# ============================================================================
def test_theme_crud(user_id):
    """Test CRUD Theme"""
    print("\n" + "=" * 60)
    print("🧪 TEST THEME CRUD")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # CREATE
        print("\n1️⃣  CREATE Theme")
        theme = Theme(
            user_id=user_id,
            name="Python Programming",
            keywords=["python", "flask", "django"],
            description="Learn Python"
        )
        session.add(theme)
        session.commit()
        print(f"✅ Theme créé : {theme.name}")
        
        # READ
        print("\n2️⃣  READ Theme")
        found = session.query(Theme).filter_by(name="Python Programming").first()
        print(f"✅ Theme trouvé : {found.name}")
        
        # TEST matches_keywords
        print("\n3️⃣  TEST matches_keywords()")
        match = found.matches_keywords(["python", "java"], threshold=0.5)
        print(f"✅ Match : {match}")
        
        # ADD/REMOVE keyword
        print("\n4️⃣  ADD/REMOVE Keywords")
        found.add_keyword("sqlalchemy")
        session.commit()
        print(f"✅ Keyword ajouté : {found.keywords}")
        
        found.remove_keyword("sqlalchemy")
        session.commit()
        print(f"✅ Keyword retiré : {found.keywords}")
        
        return theme.id
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        session.rollback()
        return None
    finally:
        session.close()


# ============================================================================
# TEST 3 : QUESTION CRUD
# ============================================================================
def test_question_crud(theme_id):
    """Test CRUD Question"""
    print("\n" + "=" * 60)
    print("🧪 TEST QUESTION CRUD")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # CREATE Quiz
        print("\n1️⃣  CREATE Quiz Question")
        quiz = Question(
            theme_id=theme_id,
            type=QuestionType.QUIZ,
            question_text="Quel framework pour les APIs ?",
            difficulty=Difficulty.EASY,
            explanation="Flask est un micro-framework"
        )
        session.add(quiz)
        session.commit()
        print(f"✅ Quiz créé : {quiz.type.value}")
        
        # CREATE Flashcard
        print("\n2️⃣  CREATE Flashcard")
        flashcard = Question(
            theme_id=theme_id,
            type=QuestionType.FLASHCARD,
            question_text="Qu'est-ce que SQLAlchemy ?",
            difficulty=Difficulty.MEDIUM
        )
        session.add(flashcard)
        session.commit()
        print(f"✅ Flashcard créée : {flashcard.type.value}")
        
        # TEST is_quiz / is_flashcard
        print("\n3️⃣  TEST is_quiz() / is_flashcard()")
        print(f"✅ quiz.is_quiz() : {quiz.is_quiz()}")
        print(f"✅ flashcard.is_flashcard() : {flashcard.is_flashcard()}")
        
        # TEST increment_usage & success_rate
        print("\n4️⃣  TEST increment_usage()")
        quiz.increment_usage(is_correct=True)
        quiz.increment_usage(is_correct=True)
        quiz.increment_usage(is_correct=False)
        session.commit()
        print(f"✅ Success rate : {quiz.get_success_rate():.1f}%")
        
        return quiz.id, flashcard.id
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        session.rollback()
        return None, None
    finally:
        session.close()


# ============================================================================
# TEST 4 : ANSWER CRUD
# ============================================================================
def test_answer_crud(question_id):
    """Test CRUD Answer"""
    print("\n" + "=" * 60)
    print("🧪 TEST ANSWER CRUD")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # CREATE Answers
        print("\n1️⃣  CREATE Answers")
        answers = [
            {"text": "Flask", "correct": True},
            {"text": "Django", "correct": False},
            {"text": "FastAPI", "correct": False},
            {"text": "Pyramid", "correct": False}
        ]
        
        for i, ans in enumerate(answers):
            answer = Answer(
                question_id=question_id,
                answer_text=ans["text"],
                is_correct=ans["correct"],
                order_position=i
            )
            session.add(answer)
        
        session.commit()
        print(f"✅ {len(answers)} réponses créées")
        
        # READ
        print("\n2️⃣  READ Answers")
        found_answers = session.query(Answer).filter_by(question_id=question_id).all()
        for a in found_answers:
            symbol = "✓" if a.is_correct else "✗"
            print(f"   {symbol} {a.answer_text}")
        
        # UPDATE - mark_as_correct
        print("\n3️⃣  TEST mark_as_correct()")
        wrong_answer = found_answers[1]
        wrong_answer.mark_as_correct()
        session.commit()
        print(f"✅ Réponse marquée correcte : {wrong_answer.is_correct}")
        
        return found_answers[0].id
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        session.rollback()
        return None
    finally:
        session.close()


# ============================================================================
# TEST 5 : SESSION CRUD
# ============================================================================
def test_session_crud(user_id, theme_id, question_ids):
    """Test CRUD Session"""
    print("\n" + "=" * 60)
    print("🧪 TEST SESSION CRUD")
    print("=" * 60)
    
    session = SessionLocal()
    
    try:
        # CREATE
        print("\n1️⃣  CREATE Session")
        quiz_session = Session(
            user_id=user_id,
            theme_id=theme_id,
            type=SessionType.QUIZ,
            questions_count=len(question_ids),
            questions_ids=question_ids
        )
        session.add(quiz_session)
        session.commit()
        print(f"✅ Session créée : {quiz_session.type.value}")
        print(f"   Is completed : {quiz_session.is_completed()}")
        
        # READ
        print("\n2️⃣  READ Session")
        found = session.query(Session).filter_by(user_id=user_id).first()
        print(f"✅ Session trouvée : {found}")
        
        # COMPLETE SESSION
        print("\n3️⃣  COMPLETE Session")
        found.complete_session(score=7, max_score=10)
        session.commit()
        print(f"✅ Score : {found.score}/{found.max_score}")
        print(f"   Success rate : {found.get_success_rate()}%")
        print(f"   Is completed : {found.is_completed()}")
        
        # ADD QUESTION ID
        print("\n4️⃣  ADD Question ID")
        found.add_question_id("new-q-123")
        session.commit()
        print(f"✅ Question ajoutée : {len(found.questions_ids)} questions")
        
        return quiz_session.id
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        session.rollback()
        return None
    finally:
        session.close()


# ============================================================================
# MAIN
# ============================================================================
def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "=" * 60)
    print("🚀 TESTS CRUD - ARCHITECTURE HBNB")
    print("=" * 60 + "\n")
    
    # Test User
    user_id = test_user_crud()
    if not user_id:
        print("\n❌ ÉCHEC User")
        return
    
    # Test Theme
    theme_id = test_theme_crud(user_id)
    if not theme_id:
        print("\n❌ ÉCHEC Theme")
        return
    
    # Test Question
    quiz_id, flashcard_id = test_question_crud(theme_id)
    if not quiz_id:
        print("\n❌ ÉCHEC Question")
        return
    
    # Test Answer
    answer_id = test_answer_crud(quiz_id)
    if not answer_id:
        print("\n❌ ÉCHEC Answer")
        return
    
    # Test Session
    session_id = test_session_crud(user_id, theme_id, [quiz_id, flashcard_id])
    if not session_id:
        print("\n❌ ÉCHEC Session")
        return
    
    # RÉSUMÉ
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS ONT RÉUSSI !")
    print("=" * 60)
    print(f"\n📊 IDs créés :")
    print(f"   User       : {user_id}")
    print(f"   Theme      : {theme_id}")
    print(f"   Quiz       : {quiz_id}")
    print(f"   Flashcard  : {flashcard_id}")
    print(f"   Answer     : {answer_id}")
    print(f"   Session    : {session_id}")
    print("\n" + "=" * 60)
    print("Bravo Arsi !")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
