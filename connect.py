"""
Lightweight shim for local development.

This file delegates to the canonical app in `api/index.py` so that the
Flask application code lives in a single place (used by Vercel). Keeping
this shim allows you to run `python connect.py` locally as before.
"""
from api.index import app
import os


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)