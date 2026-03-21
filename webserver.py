from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "online"})

@app.route("/transcript/<filename>")
def get_transcript(filename):
    directory = os.path.join(os.getcwd(), "transcripts")
    return send_from_directory(directory, filename, mimetype='text/html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
