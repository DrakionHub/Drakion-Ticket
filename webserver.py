from flask import Flask, send_from_directory, jsonify, abort
import os

app = Flask(__name__)

TRANSCRIPTS_DIR = "transcripts"

@app.route('/health')
def health():
    try:
        exists = os.path.exists(TRANSCRIPTS_DIR)
        files = os.listdir(TRANSCRIPTS_DIR) if exists else []

        return jsonify({
            "status": "online",
            "transcripts_dir": TRANSCRIPTS_DIR,
            "dir_exists": exists,
            "files_in_dir": files
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/transcript/<filename>")
def get_transcript(filename):

    if not os.path.exists(TRANSCRIPTS_DIR):
        abort(500, f"Directory not found: {TRANSCRIPTS_DIR}")

    file_path = os.path.join(TRANSCRIPTS_DIR, filename)

    if not os.path.isfile(file_path):
        abort(404, f"File not found: {filename}")

    return send_from_directory(
        TRANSCRIPTS_DIR,
        filename,
        mimetype='text/html',
        as_attachment=False
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
