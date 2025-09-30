from flask import Flask, jsonify

# Minimal placeholder app (NOT the final implementation)
app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok", message="CI skeleton up"), 200

if __name__ == "__main__":
    # Dev server only; production setup will come later
    app.run(debug=True)
