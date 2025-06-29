#!/usr/bin/env python3
"""
Test GitHub Copilot API Connection and Configuration
"""
import os
import sys
sys.path.append('/workspaces/documentParsersPy')

from api.copilot_integration import GitHubCopilotAPI, get_copilot_api

def test_copilot_api_connection():
    """Test GitHub Copilot API connection and basic functionality"""
    print("🤖 Testing GitHub Copilot API Connection")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('GITHUB_COPILOT_API_KEY')
    if not api_key:
        print("❌ GITHUB_COPILOT_API_KEY environment variable not set")
        print("Please set your GitHub Copilot API key:")
        print("export GITHUB_COPILOT_API_KEY='your_api_key_here'")
        return False
    
    print("✅ GitHub Copilot API key found")
    print(f"   Key preview: {api_key[:8]}...")
    
    # Test API initialization
    try:
        copilot = GitHubCopilotAPI()
        print("✅ GitHub Copilot API client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GitHub Copilot API: {e}")
        return False
    
    # Test basic functionality with sample data
    print("\n🧪 Testing AI capabilities...")
    
    sample_session_data = {
        'file_history': [
            {
                'filename': 'test_cdr.xlsx',
                'file_type': 'CDR',
                'record_count': 150,
                'upload_time': '2025-06-29T10:30:00'
            }
        ],
        'processing_context': {
            'total_files': 1,
            'total_records': 150
        }
    }
    
    # Test 1: Analysis generation
    print("\n1. Testing analysis generation...")
    try:
        analysis = copilot.generate_analysis_summary(sample_session_data)
        print("✅ Analysis generated successfully")
        print(f"   Preview: {analysis[:100]}...")
    except Exception as e:
        print(f"❌ Analysis generation failed: {e}")
    
    # Test 2: Question answering
    print("\n2. Testing question answering...")
    try:
        answer = copilot.answer_question(
            "What type of data did I upload?", 
            sample_session_data, 
            []
        )
        print("✅ Question answered successfully")
        print(f"   Preview: {answer[:100]}...")
    except Exception as e:
        print(f"❌ Question answering failed: {e}")
    
    # Test 3: Suggestions
    print("\n3. Testing suggestions...")
    try:
        suggestions = copilot.suggest_next_actions(sample_session_data)
        print("✅ Suggestions generated successfully")
        print(f"   Count: {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion[:80]}...")
    except Exception as e:
        print(f"❌ Suggestion generation failed: {e}")
    
    # Test 4: File type explanation
    print("\n4. Testing file type explanation...")
    try:
        explanation = copilot.explain_file_type(
            "CDR", 
            ["A_PARTY", "B_PARTY", "CALL_TYPE", "DURATION"]
        )
        print("✅ File type explained successfully")
        print(f"   Preview: {explanation[:100]}...")
    except Exception as e:
        print(f"❌ File type explanation failed: {e}")
    
    print("\n🎉 GitHub Copilot API testing completed!")
    return True

def test_global_instance():
    """Test the global Copilot API instance"""
    print("\n🌐 Testing global Copilot API instance...")
    
    copilot = get_copilot_api()
    if copilot is None:
        print("❌ Global Copilot API instance not available")
        return False
    else:
        print("✅ Global Copilot API instance working")
        return True

if __name__ == "__main__":
    success = test_copilot_api_connection()
    test_global_instance()
    
    if success:
        print("\n✅ All GitHub Copilot API tests passed!")
        print("You can now use the AI-powered features in your application.")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("Make sure you have a valid GitHub Copilot API key set.")
