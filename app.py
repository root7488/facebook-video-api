from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Facebook Video API is running"
    })

@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "status": "OK"
    })

if __name__ == "__main__":
    app.run()
