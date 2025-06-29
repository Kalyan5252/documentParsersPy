#!/usr/bin/env python3
"""
GitHub Copilot API Key Setup Helper
"""
import os
import sys

def main():
    print("🤖 GitHub Copilot API Key Setup")
    print("=" * 40)
    
    # Check current status
    current_key = os.getenv('GITHUB_COPILOT_API_KEY')
    if current_key:
        print(f"✅ API key is already set")
        print(f"   Preview: {current_key[:8]}...")
        
        # Test the integration
        print("\n🧪 Testing current configuration...")
        try:
            sys.path.append('/workspaces/documentParsersPy')
            from api.copilot_integration import GitHubCopilotAPI
            api = GitHubCopilotAPI()
            print("✅ GitHub Copilot API initialized successfully!")
            
            # Quick test
            test_data = {
                'file_history': [{'filename': 'test.xlsx', 'file_type': 'CDR', 'record_count': 10}],
                'processing_context': {}
            }
            
            result = api.generate_analysis_summary(test_data)
            print("✅ API is working - test analysis generated!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            print("Your API key might be invalid or the service might be unavailable.")
            return False
    else:
        print("❌ GITHUB_COPILOT_API_KEY is not set")
        print("\n📋 To set your GitHub Copilot API key:")
        print("1. Get your API key from GitHub")
        print("2. Run one of these commands:")
        print(f"   export GITHUB_COPILOT_API_KEY='your_api_key_here'")
        print(f"   # OR add to .env file:")
        print(f"   echo 'GITHUB_COPILOT_API_KEY=your_api_key_here' >> .env")
        
        print("\n🔑 How to get GitHub Copilot API access:")
        print("• For GitHub Copilot Individual/Business: Contact GitHub support")
        print("• For GitHub Enterprise: Check with your organization admin")
        print("• Visit: https://docs.github.com/en/copilot")
        
        # Check if user wants to set it now
        print("\n💡 Would you like to set it now? (y/n): ", end="")
        
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                print("Enter your GitHub Copilot API key: ", end="")
                api_key = input().strip()
                
                if api_key:
                    # Set environment variable for current session
                    os.environ['GITHUB_COPILOT_API_KEY'] = api_key
                    
                    # Also write to .env file
                    with open('.env', 'a') as f:
                        f.write(f'\nGITHUB_COPILOT_API_KEY={api_key}\n')
                    
                    print("✅ API key set! Testing...")
                    
                    # Test the new key
                    try:
                        sys.path.append('/workspaces/documentParsersPy')
                        from api.copilot_integration import GitHubCopilotAPI
                        api = GitHubCopilotAPI()
                        print("✅ GitHub Copilot API initialized successfully!")
                        return True
                    except Exception as e:
                        print(f"❌ Error with new API key: {e}")
                        return False
                else:
                    print("❌ No API key provided")
                    return False
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return False
        
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Setup complete! Your GitHub Copilot API is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Restart your Flask server: python api/index.py")
        print("2. Run the full test: python test_copilot_integration.py")
        print("3. Start using AI-powered features in your app!")
    else:
        print("\n❌ Setup incomplete. Please check your API key and try again.")
        print("💡 Make sure you have valid GitHub Copilot API access.")
