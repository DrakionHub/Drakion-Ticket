from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Rota para servir os arquivos da pasta transcripts
@app.route("/transcript/<filename>")
def get_transcript(filename):
    # Obtém o caminho absoluto da pasta transcripts
    directory = os.path.join(os.getcwd(), "transcripts")
    return send_from_directory(directory, filename)

if __name__ == "__main__":
    # O Railway usa a variável de ambiente PORT, se não houver, usa 3000
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
