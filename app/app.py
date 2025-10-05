from flask import Flask, jsonify

# Minimal placeholder app (NOT the final implementation)
app = Flask(__name__)
import logging
import os
from logging.handlers import RotatingFileHandler

# Logging setup
os.makedirs("logs", exist_ok=True)
log_path = os.path.join("logs", "app.log")

handler = RotatingFileHandler(log_path, maxBytes=1048576, backupCount=3)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

@app.before_request
def _log_request():
    from flask import request
    app.logger.info("REQUEST %s %s", request.method, request.path)

@app.after_request
def _log_response(response):
    app.logger.info("RESPONSE %s %s -> %s", getattr(response, "direct_passthrough", False), response.content_type, response.status_code)
    return response


@app.get("/health")
def health():
    return jsonify(status="ok", message="CI skeleton up"), 200

if __name__ == "__main__":
    # Dev server only; production setup will come later
    app.run(debug=True)
