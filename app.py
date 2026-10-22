from flask import Flask, render_template, request, jsonify
from core import execute_task
from planner import planner

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planner')
def planner_page():
    return render_template('planner.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    try:
        reply, _ = execute_task(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Ошибка: {e}"})

@app.route('/api/plan/start', methods=['POST'])
def start_plan():
    data = request.json
    tasks = data.get('tasks', [])
    plan_id = planner.create_plan(tasks)
    return jsonify({"plan_id": plan_id})

@app.route('/api/plan/<plan_id>/status')
def plan_status(plan_id):
    status = planner.get_status(plan_id)
    if not status:
        return jsonify({"error": "План не найден"}), 404
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, port=5000)