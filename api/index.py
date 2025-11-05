from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask.logging import create_logger
import os
import sys

# Ensure project root (parent of `api/`) is on sys.path so imports like `tasks` work
# when running `api/index.py` directly or when the working directory is `api/`.
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import tasks
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app with absolute static/template paths so the app works
# reliably whether run locally or as a Vercel serverless function.
app = Flask(__name__,
           static_folder=os.path.join(root, 'static'),
           static_url_path='/static',
           template_folder=os.path.join(root, 'templates'))

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure logging
logger = create_logger(app)

# --- Homepage ---
@app.route("/", methods=['GET'])
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return str(e), 500

# --- Get all tasks ---
@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        data = tasks.load_tasks()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error loading tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Add a new task ---
@app.route("/tasks", methods=["POST"])
def add_task_api():
    try:
        new_task = request.json
        task_name = new_task.get("task", "")
        day = new_task.get("day", "today")
        priority = new_task.get("priority", "medium")
        success = tasks.add_task(task_name, day=day, priority=priority)
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Error adding task: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Remove a task ---
@app.route("/remove", methods=["POST"])
def remove_task_api():
    try:
        info = request.json
        index = info.get("index", 0)
        day = info.get("day", "today")
        result = tasks.remove_task(index, day=day)
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"Error removing task: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Clear all tasks ---
@app.route("/clear", methods=["POST"])
def clear_all_tasks():
    try:
        tasks.clear_tasks()  # clears both today and tomorrow
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error clearing tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Get random task ---
@app.route("/random_task")
def get_random_task_api():
    try:
        day = request.args.get("day", "today")
        task = tasks.get_random_task(day=day)
        return jsonify(task if task else {"task": None})
    except Exception as e:
        logger.error(f"Error getting random task: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Force HTTPS on Vercel
@app.before_request
def before_request():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page not found: {request.url}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500