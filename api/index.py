from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import os
import tempfile

# Import your existing logic directly here
try:
    from .parsers import normalize_column, detect_file_type, push_to_neo4j
    from .session_manager import session_manager
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from parsers import normalize_column, detect_file_type, push_to_neo4j
    from session_manager import session_manager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-for-sessions-2024')
CORS(app, supports_credentials=True)

@app.route('/check', methods=['GET'])
def checkapi():
    return jsonify({"success": "working"}), 200

@app.route('/parse-data', methods=['POST'])
def parse_data():
    # Get or create session
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    session_id, user_session = session_manager.get_or_create_session(session_id)
    session['session_id'] = session_id
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    print(f'got file {file} for session {session_id}')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            temp_file_path = tmp.name
            file.save(tmp.name)
            df = pd.read_excel(tmp.name).fillna("").astype(str)
            df.columns = [normalize_column(c) for c in df.columns]
            file_type = detect_file_type(df.columns)

            if file_type in {"CDR", "IPDR", "TD"}:
                push_to_neo4j(df, file_type)
                
                # Add to session memory
                file_info = {
                    'filename': file.filename,
                    'file_type': file_type,
                    'record_count': len(df),
                    'status': 'success',
                    'columns': list(df.columns)
                }
                session_manager.add_file_to_session(session_id, file_info)
                
                # Update processing context
                session_manager.update_processing_context(session_id, {
                    'last_file_type': file_type,
                    'last_record_count': len(df),
                    'total_files_processed': len(user_session['file_history']) + 1
                })
                
                # Generate AI explanation for the file type (optional)
                try:
                    ai_explanation = session_manager.explain_file_type_ai(session_id, file_type, list(df.columns))
                    file_explanation = ai_explanation.get('explanation', '') if ai_explanation else ''
                except Exception as e:
                    file_explanation = f"AI explanation unavailable: {str(e)}"
                
                return jsonify({
                    "status": "success", 
                    "file_type": file_type,
                    "session_id": session_id,
                    "record_count": len(df),
                    "columns": list(df.columns),
                    "ai_explanation": file_explanation
                }), 200
            else:
                session_manager.add_error_to_session(session_id, file.filename, f"Unknown file type. Detected columns: {list(df.columns)}")
                return jsonify({"error": "Unknown file type", "detected_columns": list(df.columns)}), 400
                
    except Exception as e:
        # Log error to session
        error_msg = str(e)
        session_manager.add_error_to_session(session_id, file.filename, error_msg)
        return jsonify({"error": error_msg, "session_id": session_id}), 500
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.route('/session/history', methods=['GET'])
def get_session_history():
    """Get session history and conversation"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    history = session_manager.get_session_history(session_id)
    if history is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(history), 200

@app.route('/session/stats', methods=['GET'])
def get_session_stats():
    """Get session statistics"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    stats = session_manager.get_session_stats(session_id)
    if stats is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(stats), 200

@app.route('/session/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up old sessions"""
    max_age_hours = request.json.get('max_age_hours', 24) if request.is_json else 24
    cleaned_count = session_manager.cleanup_old_sessions(max_age_hours)
    return jsonify({"cleaned_sessions": cleaned_count}), 200

@app.route('/session/memory', methods=['GET'])
def get_session_memory():
    """Get session conversation memory"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    # Create session if it doesn't exist
    session_id, user_session = session_manager.get_or_create_session(session_id)
    messages = user_session['memory'].chat_memory.messages
    
    return jsonify({
        "session_id": session_id,
        "memory_type": "ConversationBufferMemory",
        "message_count": len(messages),
        "messages": [
            {
                "type": "human" if hasattr(msg, '__class__') and 'Human' in msg.__class__.__name__ else "ai",
                "content": msg.content,
                "timestamp": getattr(msg, 'timestamp', None)
            }
            for msg in messages
        ]
    }), 200

@app.route('/session/ai/analysis', methods=['GET'])
def get_ai_analysis():
    """Get AI-powered analysis of session data"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    analysis = session_manager.get_ai_analysis(session_id)
    if analysis is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(analysis), 200

@app.route('/session/ai/ask', methods=['POST'])
def ask_ai_question():
    """Ask AI a question about the session data"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    question = request.json.get('question')
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    result = session_manager.ask_ai_question(session_id, question)
    if result is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(result), 200

@app.route('/session/ai/suggestions', methods=['GET'])
def get_ai_suggestions():
    """Get AI-powered suggestions for next actions"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    suggestions = session_manager.get_ai_suggestions(session_id)
    if suggestions is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(suggestions), 200

@app.route('/session/ai/explain/<file_type>', methods=['GET'])
def explain_file_type():
    """Get AI explanation of a file type"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    file_type = request.view_args['file_type']
    columns = request.args.getlist('columns')  # Accept columns as query parameters
    
    explanation = session_manager.explain_file_type_ai(session_id, file_type, columns)
    if explanation is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(explanation), 200

@app.route('/session/ai/chat', methods=['POST'])
def ai_chat():
    """General AI chat endpoint for conversational interaction"""
    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    message = request.json.get('message')
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Use the ask_ai_question method for general chat
    result = session_manager.ask_ai_question(session_id, message)
    if result is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "message": message,
        "response": result.get("answer"),
        "timestamp": result.get("timestamp")
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
