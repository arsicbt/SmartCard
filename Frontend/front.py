"""
Flask application pour LearnFlow AI
Plateforme d'apprentissage avec flashcards et quiz
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
