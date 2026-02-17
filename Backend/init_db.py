from sqlalchemy import create_engine
from Models.tablesSchema import Base 

from Models.userModel import User
from Models.themeModel import Theme
from Models.questionModel import Question
from Models.answerModel import Answer
from Models.sessionModel import Session

DATABASE_URL = 'sqlite:///smartcard.db'

engine = create_engine(DATABASE_URL, echo=True)

print("Dropping existing tables...")
Base.metadata.drop_all(engine)

print("Creating tables...")
Base.metadata.create_all(engine)

print("Database initialized successfully!")
