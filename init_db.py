from sqlalchemy import create_engine
from Models.tablesSchema import Base  # <-- IMPORT CORRECT


DATABASE_URL = 'sqlite:///smartcard.db'

engine = create_engine(DATABASE_URL, echo=True)

print("Dropping existing tables...")
Base.metadata.drop_all(engine)

print("Creating tables...")
Base.metadata.create_all(engine)

print("Database initialized successfully!")
