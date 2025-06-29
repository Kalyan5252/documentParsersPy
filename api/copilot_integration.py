import os
import openai
from typing import Dict, List, Optional
import json

class GitHubCopilotAPI:
    """
    GitHub Copilot API integration for intelligent conversation capabilities
    Supports multiple AI providers as fallback options
    """
    
    def __init__(self):
        self.api_key = os.getenv('GITHUB_COPILOT_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key and not self.openai_key:
            raise ValueError("Either GITHUB_COPILOT_API_KEY or OPENAI_API_KEY environment variable is required")
        
        # Try GitHub Copilot API first, fallback to OpenAI
        self.provider = "github_copilot"
        self.client = None
        self.model = "gpt-4"
        
        if self.api_key:
            try:
                # Configure for GitHub Copilot API
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.githubcopilot.com"
                )
                self.provider = "github_copilot"
                self.model = "gpt-4"
            except Exception as e:
                print(f"GitHub Copilot API initialization failed: {e}")
                self.client = None
        
        # Fallback to OpenAI if GitHub Copilot fails or is unavailable
        if not self.client and self.openai_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_key)
                self.provider = "openai"
                self.model = "gpt-4o"
                print("Using OpenAI API as fallback")
            except Exception as e:
                print(f"OpenAI API initialization failed: {e}")
        
        if not self.client:
            raise ValueError("Failed to initialize any AI provider")
        
    def generate_analysis_summary(self, session_data: Dict) -> str:
        """
        Generate an intelligent analysis summary of the session data
        """
        file_history = session_data.get('file_history', [])
        processing_context = session_data.get('processing_context', {})
        
        # Prepare context for the AI
        context = self._prepare_analysis_context(file_history, processing_context)
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert telecommunications data analyst. 
                Analyze file processing sessions and provide intelligent insights about:
                - Data patterns and trends
                - File type distributions  
                - Processing statistics
                - Potential security or investigative insights
                - Recommendations for further analysis
                
                Be concise but insightful. Focus on actionable intelligence."""
            },
            {
                "role": "user", 
                "content": f"Analyze this session data: {context}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Analysis generation failed using {self.provider}: {str(e)}"
            print(error_msg)
            return error_msg
    
    def answer_question(self, question: str, session_data: Dict, conversation_history: List) -> str:
        """
        Answer user questions about their data processing session
        """
        # Prepare comprehensive context
        context = self._prepare_conversation_context(session_data, conversation_history)
        
        messages = [
            {
                "role": "system", 
                "content": """You are an AI assistant specialized in telecommunications data analysis.
                You help users understand their data processing sessions, file uploads, and analysis results.
                
                Capabilities:
                - Explain file types (CDR, IPDR, TD)
                - Provide insights on call patterns, network usage
                - Help with troubleshooting data issues
                - Suggest analysis approaches
                - Answer questions about Neo4j graph data
                
                Be helpful, accurate, and focused on telecommunications/investigative contexts."""
            },
            {
                "role": "user",
                "content": f"Session context: {context}\n\nUser question: {question}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your question using {self.provider}: {str(e)}"
    
    def suggest_next_actions(self, session_data: Dict) -> List[str]:
        """
        Suggest intelligent next actions based on processed data
        """
        file_history = session_data.get('file_history', [])
        processing_context = session_data.get('processing_context', {})
        
        context = self._prepare_analysis_context(file_history, processing_context)
        
        messages = [
            {
                "role": "system",
                "content": """You are a telecommunications data analysis expert.
                Based on processed files and session data, suggest 3-5 specific next actions
                that would be valuable for investigation or analysis.
                
                Format as a JSON array of strings. Be specific and actionable."""
            },
            {
                "role": "user",
                "content": f"Suggest next actions for this session: {context}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.5
            )
            
            # Try to parse as JSON, fallback to text split
            try:
                suggestions = json.loads(response.choices[0].message.content)
                return suggestions if isinstance(suggestions, list) else [response.choices[0].message.content]
            except json.JSONDecodeError:
                # Fallback: split by lines and clean up
                text = response.choices[0].message.content
                return [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
                
        except Exception as e:
            return [f"Unable to generate suggestions: {str(e)}"]
    
    def explain_file_type(self, file_type: str, columns: List[str]) -> str:
        """
        Explain what a specific file type contains and its significance
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert in telecommunications data formats.
                Explain file types clearly and concisely, focusing on:
                - What the data represents
                - Key fields and their meaning
                - Typical use cases for analysis
                - Investigation/security relevance"""
            },
            {
                "role": "user",
                "content": f"Explain {file_type} file type with these columns: {columns}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=250,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Unable to explain file type: {str(e)}"
    
    def _prepare_analysis_context(self, file_history: List, processing_context: Dict) -> str:
        """Prepare context string for analysis"""
        context_parts = []
        
        # File summary
        if file_history:
            file_types = {}
            total_records = 0
            for file_info in file_history:
                file_type = file_info.get('file_type', 'UNKNOWN')
                file_types[file_type] = file_types.get(file_type, 0) + 1
                total_records += file_info.get('record_count', 0)
            
            context_parts.append(f"Files processed: {len(file_history)}")
            context_parts.append(f"File types: {file_types}")
            context_parts.append(f"Total records: {total_records}")
        
        # Processing context
        if processing_context:
            context_parts.append(f"Processing context: {processing_context}")
        
        return " | ".join(context_parts)
    
    def _prepare_conversation_context(self, session_data: Dict, conversation_history: List) -> str:
        """Prepare context for conversation"""
        context_parts = []
        
        # Recent conversation (last 5 messages)
        if conversation_history:
            recent_conv = conversation_history[-5:]
            context_parts.append(f"Recent conversation: {recent_conv}")
        
        # Session summary
        context_parts.append(self._prepare_analysis_context(
            session_data.get('file_history', []),
            session_data.get('processing_context', {})
        ))
        
        return " | ".join(context_parts)

# Global instance
copilot_api = None

def get_copilot_api():
    """Get or create GitHub Copilot API instance"""
    global copilot_api
    if copilot_api is None:
        try:
            copilot_api = GitHubCopilotAPI()
        except ValueError as e:
            print(f"Warning: GitHub Copilot API not available: {e}")
            return None
    return copilot_api
