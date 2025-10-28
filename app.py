from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

# Load quiz data
with open("quiz_data.json", "r") as f:
    quiz_data = json.load(f)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get-quiz', methods=['GET'])
def get_quiz():
    return jsonify(quiz_data)

@app.route('/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    score = 0
    for i, q in enumerate(quiz_data):
        if data.get(str(i)) == q['answer']:
            score += 1
    return jsonify({"score": score, "total": len(quiz_data)})

if __name__ == "__main__":
    app.run(debug=True)
