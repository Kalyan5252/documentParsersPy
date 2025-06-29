from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import tempfile
import sys

# Add the api directory to Python path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

# Import your existing logic from the api directory
from parsers import normalize_column, detect_file_type, push_to_neo4j

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Document Parser API is running", "status": "success"}), 200

@app.route('/check', methods=['GET'])
def checkapi():
    return jsonify({"success": "working"}), 200

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
    finally:
        # Clean up the temporary file
        if 'tmp' in locals():
            try:
                os.unlink(tmp.name)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True)
