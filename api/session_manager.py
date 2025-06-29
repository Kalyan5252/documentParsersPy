from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from collections import defaultdict
import uuid
from datetime import datetime, timedelta
try:
    from .copilot_integration import get_copilot_api
except ImportError:
    from copilot_integration import get_copilot_api

class SessionManager:
    def __init__(self):
        self.sessions = defaultdict(lambda: {
            'memory': ConversationBufferMemory(return_messages=True),
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'file_history': [],
            'processing_context': {}
        })
    
    def get_or_create_session(self, session_id=None):
        """Get existing session or create new one"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id]['last_activity'] = datetime.now()
        return session_id, self.sessions[session_id]
    
    def add_file_to_session(self, session_id, file_info):
        """Add file processing info to session memory"""
        session = self.sessions[session_id]
        session['file_history'].append({
            'filename': file_info.get('filename'),
            'file_type': file_info.get('file_type'),
            'processed_at': datetime.now().isoformat(),
            'status': file_info.get('status'),
            'record_count': file_info.get('record_count', 0),
            'columns': file_info.get('columns', [])
        })
        
        # Add to conversation memory
        user_message = f"Processed file: {file_info.get('filename')} (Type: {file_info.get('file_type')})"
        ai_message = f"Successfully processed {file_info.get('file_type')} file with {file_info.get('record_count', 0)} records"
        
        session['memory'].chat_memory.add_user_message(user_message)
        session['memory'].chat_memory.add_ai_message(ai_message)
    
    def add_error_to_session(self, session_id, filename, error_message):
        """Add error information to session memory"""
        session = self.sessions[session_id]
        session['memory'].chat_memory.add_user_message(f"Error processing {filename}")
        session['memory'].chat_memory.add_ai_message(f"Error: {error_message}")
    
    def get_session_history(self, session_id):
        """Get session history and conversation"""
        if session_id not in self.sessions:
            return None
        
        user_session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": user_session['created_at'].isoformat(),
            "last_activity": user_session['last_activity'].isoformat(),
            "file_history": user_session['file_history'],
            "conversation": [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai", 
                    "content": msg.content
                }
                for msg in user_session['memory'].chat_memory.messages
            ],
            "processing_context": user_session['processing_context']
        }
    
    def update_processing_context(self, session_id, context_data):
        """Update processing context for session"""
        session = self.sessions[session_id]
        session['processing_context'].update(context_data)
    
    def cleanup_old_sessions(self, max_age_hours=24):
        """Remove sessions older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = [
            sid for sid, session in self.sessions.items() 
            if session['last_activity'] < cutoff_time
        ]
        for sid in expired_sessions:
            del self.sessions[sid]
        return len(expired_sessions)
    
    def get_session_stats(self, session_id):
        """Get statistics for a session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        file_types = {}
        total_records = 0
        
        for file_info in session['file_history']:
            file_type = file_info.get('file_type', 'UNKNOWN')
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_records += file_info.get('record_count', 0)
        
        return {
            "files_processed": len(session['file_history']),
            "file_types": file_types,
            "total_records": total_records,
            "session_duration": (session['last_activity'] - session['created_at']).total_seconds(),
            "conversation_messages": len(session['memory'].chat_memory.messages)
        }
    
    def get_ai_analysis(self, session_id):
        """Get AI-powered analysis of session data using GitHub Copilot"""
        if session_id not in self.sessions:
            return None
        
        copilot = get_copilot_api()
        if not copilot:
            return {"error": "GitHub Copilot API not available"}
        
        session = self.sessions[session_id]
        analysis = copilot.generate_analysis_summary(session)
        
        # Add AI analysis to conversation memory
        session['memory'].chat_memory.add_user_message("Generate analysis summary")
        session['memory'].chat_memory.add_ai_message(analysis)
        
        return {"analysis": analysis, "timestamp": datetime.now().isoformat()}
    
    def ask_ai_question(self, session_id, question):
        """Ask GitHub Copilot a question about the session data"""
        if session_id not in self.sessions:
            return None
        
        copilot = get_copilot_api()
        if not copilot:
            return {"error": "GitHub Copilot API not available"}
        
        session = self.sessions[session_id]
        conversation_history = [
            {"type": "human" if isinstance(msg, HumanMessage) else "ai", "content": msg.content}
            for msg in session['memory'].chat_memory.messages
        ]
        
        answer = copilot.answer_question(question, session, conversation_history)
        
        # Add to conversation memory
        session['memory'].chat_memory.add_user_message(question)
        session['memory'].chat_memory.add_ai_message(answer)
        
        return {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_ai_suggestions(self, session_id):
        """Get AI-powered suggestions for next actions"""
        if session_id not in self.sessions:
            return None
        
        copilot = get_copilot_api()
        if not copilot:
            return {"error": "GitHub Copilot API not available"}
        
        session = self.sessions[session_id]
        suggestions = copilot.suggest_next_actions(session)
        
        # Add to conversation memory
        session['memory'].chat_memory.add_user_message("What should I do next?")
        suggestions_text = "Here are my suggestions:\n" + "\n".join(f"• {s}" for s in suggestions)
        session['memory'].chat_memory.add_ai_message(suggestions_text)
        
        return {
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def explain_file_type_ai(self, session_id, file_type, columns):
        """Get AI explanation of a file type"""
        if session_id not in self.sessions:
            return None
        
        copilot = get_copilot_api()
        if not copilot:
            return {"error": "GitHub Copilot API not available"}
        
        session = self.sessions[session_id]
        explanation = copilot.explain_file_type(file_type, columns)
        
        # Add to conversation memory
        session['memory'].chat_memory.add_user_message(f"Explain {file_type} file type")
        session['memory'].chat_memory.add_ai_message(explanation)
        
        return {
            "file_type": file_type,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }

# Global session manager instance
session_manager = SessionManager()
