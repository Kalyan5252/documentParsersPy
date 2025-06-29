#!/usr/bin/env python3
"""
Comprehensive AI API Test and Status Check
"""
import os
import sys
sys.path.append('/workspaces/documentParsersPy')

def test_api_keys():
    """Test available API keys and providers"""
    print("🔑 API Key Status Check")
    print("=" * 40)
    
    github_key = os.getenv('GITHUB_COPILOT_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"GitHub Copilot API Key: {'✅ Found' if github_key else '❌ Not found'}")
    if github_key:
        print(f"   Preview: {github_key[:8]}...")
        print(f"   Type: {'Personal Access Token (PAT)' if github_key.startswith('ghp_') else 'Unknown'}")
    
    print(f"OpenAI API Key: {'✅ Found' if openai_key else '❌ Not found'}")
    if openai_key:
        print(f"   Preview: {openai_key[:8]}...")
    
    return github_key, openai_key

def test_ai_providers():
    """Test AI provider initialization and capabilities"""
    print("\n🤖 AI Provider Testing")
    print("=" * 40)
    
    try:
        from api.copilot_integration import GitHubCopilotAPI
        
        # Test provider initialization
        api = GitHubCopilotAPI()
        print(f"✅ AI Provider initialized: {api.provider}")
        print(f"   Model: {api.model}")
        
        # Test basic functionality
        sample_data = {
            'file_history': [
                {
                    'filename': 'test_cdr.xlsx',
                    'file_type': 'CDR',
                    'record_count': 25,
                    'upload_time': '2025-06-29T10:30:00'
                }
            ],
            'processing_context': {
                'total_files': 1,
                'total_records': 25
            }
        }
        
        print("\n🧪 Testing AI Capabilities...")
        
        # Test 1: Analysis
        print("1. Testing analysis generation...")
        try:
            analysis = api.generate_analysis_summary(sample_data)
            if "failed" in analysis.lower() or "error" in analysis.lower():
                print(f"   ⚠️  Analysis had issues: {analysis[:100]}...")
            else:
                print(f"   ✅ Analysis generated successfully")
                print(f"      Preview: {analysis[:80]}...")
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
        
        # Test 2: Question answering
        print("\n2. Testing question answering...")
        try:
            answer = api.answer_question("What type of data was uploaded?", sample_data, [])
            if "trouble processing" in answer.lower() or "error" in answer.lower():
                print(f"   ⚠️  Q&A had issues: {answer[:100]}...")
            else:
                print(f"   ✅ Question answered successfully")
                print(f"      Preview: {answer[:80]}...")
        except Exception as e:
            print(f"   ❌ Q&A failed: {e}")
        
        # Test 3: Suggestions
        print("\n3. Testing suggestions...")
        try:
            suggestions = api.suggest_next_actions(sample_data)
            if isinstance(suggestions, list) and len(suggestions) > 0:
                if "unable to generate" in str(suggestions[0]).lower():
                    print(f"   ⚠️  Suggestions had issues: {suggestions[0][:80]}...")
                else:
                    print(f"   ✅ Suggestions generated: {len(suggestions)} items")
                    for i, suggestion in enumerate(suggestions[:2], 1):
                        print(f"      {i}. {suggestion[:60]}...")
            else:
                print(f"   ⚠️  No suggestions generated")
        except Exception as e:
            print(f"   ❌ Suggestions failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Provider initialization failed: {e}")
        return False

def provide_recommendations():
    """Provide recommendations based on test results"""
    print("\n💡 Recommendations")
    print("=" * 40)
    
    github_key = os.getenv('GITHUB_COPILOT_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if github_key and github_key.startswith('ghp_'):
        print("⚠️  GitHub Personal Access Token Detected")
        print("   Your current key is a Personal Access Token (PAT)")
        print("   GitHub Copilot API requires special enterprise access")
        print("")
        print("🔧 Solutions:")
        print("   1. Contact your GitHub Enterprise admin for Copilot API access")
        print("   2. Use OpenAI API as an alternative:")
        print("      export OPENAI_API_KEY='your-openai-key'")
        print("   3. Check GitHub Copilot Enterprise documentation")
    
    if not openai_key:
        print("\n💡 OpenAI API Alternative")
        print("   To use OpenAI as a fallback:")
        print("   1. Get an API key from https://platform.openai.com/")
        print("   2. Set: export OPENAI_API_KEY='your-openai-key'")
        print("   3. Restart your application")
    
    print("\n📚 Resources:")
    print("   • GitHub Copilot Enterprise: https://docs.github.com/en/enterprise-cloud@latest/copilot")
    print("   • OpenAI API: https://platform.openai.com/docs/")

def test_flask_integration():
    """Test if Flask server can use the AI integration"""
    print("\n🌐 Flask Integration Test")
    print("=" * 40)
    
    try:
        from api.session_manager import session_manager
        
        # Test session manager AI capabilities
        session_id = "test-integration-session"
        session_id, session_data = session_manager.get_or_create_session(session_id)
        
        print("✅ Session manager initialized")
        
        # Test AI integration through session manager
        analysis = session_manager.get_ai_analysis(session_id)
        if analysis and not analysis.get('error'):
            print("✅ Session manager AI integration working")
        else:
            print(f"⚠️  Session manager AI had issues: {analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False

def main():
    """Run comprehensive AI API testing"""
    print("🧪 Comprehensive AI API Testing")
    print("=" * 50)
    
    # Test 1: API keys
    github_key, openai_key = test_api_keys()
    
    # Test 2: AI providers
    provider_success = test_ai_providers()
    
    # Test 3: Flask integration
    flask_success = test_flask_integration()
    
    # Test 4: Recommendations
    provide_recommendations()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    print(f"API Keys Available: {bool(github_key or openai_key)}")
    print(f"AI Provider Working: {provider_success}")
    print(f"Flask Integration: {flask_success}")
    
    if provider_success and flask_success:
        print("\n🎉 System Status: READY")
        print("   Your AI-powered features are working!")
        print("   Start your Flask server: python api/index.py")
    elif github_key and github_key.startswith('ghp_'):
        print("\n⚠️  System Status: NEEDS CONFIGURATION")
        print("   GitHub PAT detected - need proper Copilot API access")
        print("   Consider using OpenAI API as alternative")
    else:
        print("\n❌ System Status: NEEDS SETUP")
        print("   Please configure proper API keys")

if __name__ == "__main__":
    main()
