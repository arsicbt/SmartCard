from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS

import os

from Api.userRoutes import users_bp
from Api.themeRoutes import theme_bp
from Api.questionRoutes import question_bp
from Api.answerRoutes import answer_bp
from Api.sessionRoutes import session_bp
from Api.authRoutes import auth_bp


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../Frontend/Templates"),
    static_folder=os.path.join(BASE_DIR, "../Frontend/Static")
)
CORS(app)

# **************************************
# Route temporaire du front 
# **************************************
@app.route("/")
def home():
    return render_template(
        "index.html",
        username="Arsi", 
        total_cards=342,
        total_quiz=48,
        correct_answers=1248
    )

@app.route("/cards")
def cards():
    return render_template("cards.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/logout")
def logout():
    return redirect(url_for("home"))

app.register_blueprint(users_bp)
app.register_blueprint(theme_bp)
app.register_blueprint(question_bp)
app.register_blueprint(answer_bp)
app.register_blueprint(session_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
