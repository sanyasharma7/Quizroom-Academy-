from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# Load quizzes dynamically
def load_quiz(exam):
    path = os.path.join("quizzes", f"{exam}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get-quiz/<exam>', methods=['GET'])
def get_quiz(exam):
    quiz_data = load_quiz(exam)
    return jsonify(quiz_data)

@app.route('/submit/<exam>', methods=['POST'])
def submit_quiz(exam):
    data = request.json
    quiz_data = load_quiz(exam)
    score = 0
    for i, q in enumerate(quiz_data):
        if data.get(str(i)) == q['answer']:
            score += 1
    return jsonify({"score": score, "total": len(quiz_data)})

if __name__ == "__main__":
    app.run(debug=True)
