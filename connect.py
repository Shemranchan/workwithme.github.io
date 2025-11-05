from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask.logging import create_logger
import tasks
import os
import sys
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__,
           static_folder='static',
           static_url_path='/static',
           template_folder='templates')

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure logging
logger = create_logger(app)

# Remove duplicate debug settings

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

# Only run debug server locally
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page not found: {request.url}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500