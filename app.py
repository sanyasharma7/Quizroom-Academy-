# app.py
from flask import Flask, render_template, jsonify, request
import json, os
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Add in Render environment

# Load quiz
def load_quiz(exam, subtopic):
    path = os.path.join("quizzes", exam, f"{subtopic}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_subtopics/<exam>')
def get_subtopics(exam):
    path = os.path.join("quizzes", exam)
    if os.path.exists(path):
        return jsonify([f.replace(".json","") for f in os.listdir(path)])
    return jsonify([])

@app.route('/get-quiz/<exam>/<subtopic>')
def get_quiz(exam, subtopic):
    return jsonify(load_quiz(exam, subtopic))

@app.route('/submit/<exam>/<subtopic>', methods=['POST'])
def submit_quiz(exam, subtopic):
    data = request.json
    quiz_data = load_quiz(exam, subtopic)
    score = 0
    incorrect_questions = []

    for i, q in enumerate(quiz_data):
        if data.get(str(i)) == q['answer']:
            score += 1
        else:
            incorrect_questions.append({
                "question": q['question'],
                "correct": q['answer']
            })

    summary_text = generate_ai_summary(score, len(quiz_data), incorrect_questions)
    
    return jsonify({
        "score": score,
        "total": len(quiz_data),
        "incorrect_questions": incorrect_questions,
        "ai_summary": summary_text
    })

def generate_ai_summary(score, total, incorrect_questions):
    if len(incorrect_questions) == 0:
        return "Excellent! You answered all questions correctly. Keep up the good work!"
    weak_questions_text = "\n".join([f"Q: {q['question']} | Correct: {q['correct']}" for q in incorrect_questions])
    prompt = f"""
You are a helpful study assistant. 
A student scored {score}/{total}. Here are questions they got wrong:
{weak_questions_text}
Generate a friendly, actionable summary for the student.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=200
        )
        return response['choices'][0]['message']['content']
    except:
        return "Could not generate AI summary."
