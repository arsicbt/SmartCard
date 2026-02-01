from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = 'sqlite:///smartcard.db'

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return {
        "status": "ok"
    }, 200
    

# Engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
