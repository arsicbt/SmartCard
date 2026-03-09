"""Point d'entrée principal de l'application Flask SmartCard."""
from Api.authRoutes import auth_bp
from Api.sessionRoutes import session_bp
from Api.answerRoutes import answer_bp
from Api.questionRoutes import question_bp
from Api.themeRoutes import theme_bp
from Api.userRoutes import users_bp
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)

app.register_blueprint(users_bp)
app.register_blueprint(theme_bp)
app.register_blueprint(question_bp)
app.register_blueprint(answer_bp)
app.register_blueprint(session_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=False)
