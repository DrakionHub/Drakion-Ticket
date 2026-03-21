from flask import Flask, send_from_directory, jsonify, abort
import os

app = Flask(__name__)

# Pega o mount path do Railway (se não tiver, fallback para /transcripts)
TRANSCRIPTS_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/transcripts")
if not TRANSCRIPTS_DIR.endswith("/transcripts"):
    TRANSCRIPTS_DIR = os.path.join(TRANSCRIPTS_DIR, "transcripts")  # ajusta se montou em /data

print(f"[DEBUG] Usando TRANSCRIPTS_DIR: {TRANSCRIPTS_DIR}")
print(f"[DEBUG] CWD: {os.getcwd()}")
print(f"[DEBUG] Files in dir: {os.listdir(TRANSCRIPTS_DIR) if os.path.exists(TRANSCRIPTS_DIR) else 'DIR NOT FOUND'}")

@app.route('/health')
def health():
    try:
        exists = os.path.exists(TRANSCRIPTS_DIR)
        files = os.listdir(TRANSCRIPTS_DIR) if exists else []
        return jsonify({
            "status": "online",
            "cwd": os.getcwd(),
            "transcripts_dir": TRANSCRIPTS_DIR,
            "dir_exists": exists,
            "files_in_dir": files,
            "python_version": os.sys.version
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
    try:
        return send_from_directory(TRANSCRIPTS_DIR, filename, mimetype='text/html', as_attachment=False)
    except Exception as e:
        abort(500, f"Send error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"[DEBUG] Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port)  # debug=False para produção
