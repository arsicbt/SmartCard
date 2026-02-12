from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = 'sqlite:///smartcard.db'

app = Flask(__name__)
CORS(app)

# Engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
