from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import tempfile

# Import your existing logic directly here
from parsers import normalize_column, detect_file_type, push_to_neo4j

app = Flask(__name__)
CORS(app)

@app.route('/check', methods=['GET'])
def checkapi():
    return jsonify({"success": "working"}), 400

@app.route('/parse-data', methods=['POST'])
def parse_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    print(f'got file {file}')
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            file.save(tmp.name)
            df = pd.read_excel(tmp.name).fillna("").astype(str)
            df.columns = [normalize_column(c) for c in df.columns]
            file_type = detect_file_type(df.columns)

            if file_type in {"CDR", "IPDR", "TD"}:
                push_to_neo4j(df, file_type)
                return jsonify({"status": "success", "file_type": file_type}), 200
            else:
                return jsonify({"error": "Unknown file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
