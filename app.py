from flask import Flask, render_template, jsonify, request
import json
import os
import openai  # pip install openai

app = Flask(__name__)

# Set your OpenAI API key as environment variable in Render: OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    incorrect_questions = []

    for i, q in enumerate(quiz_data):
        if data.get(str(i)) == q['answer']:
            score += 1
        else:
            incorrect_questions.append({
                "question": q['question'],
                "correct": q['answer']
            })

    # Generate AI summary
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
A student took a quiz and scored {score}/{total}. 
Here are the questions they got wrong:
{weak_questions_text}

Generate a friendly, actionable summary for the student:
- Highlight weak topics
- Suggest how to revise
- Motivate them to improve
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=200
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "Could not generate AI summary at this moment."
