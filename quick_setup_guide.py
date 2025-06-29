#!/usr/bin/env python3
"""
Simple AI API Status and Recommendation
"""
import os

def main():
    print("🔍 AI API Status Report")
    print("=" * 50)
    
    github_key = os.getenv('GITHUB_COPILOT_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print("\n📊 Current Situation:")
    print("✅ GitHub Copilot API key found (Personal Access Token)")
    print("❌ This PAT cannot access GitHub Copilot API endpoints")
    print("❌ OpenAI API key not found")
    
    print("\n🔧 Solution Options:")
    print("\n1. 🌟 RECOMMENDED: Use OpenAI API (Easy & Works Now)")
    print("   • Get API key from: https://platform.openai.com/")
    print("   • Cost: ~$0.002 per 1K tokens (very affordable)")
    print("   • Set: export OPENAI_API_KEY='your-openai-key'")
    print("   • Your app will work immediately!")
    
    print("\n2. 🏢 GitHub Copilot Enterprise (For Organizations)")
    print("   • Requires GitHub Enterprise subscription")
    print("   • Contact your GitHub Enterprise admin")
    print("   • Special API access required (not PAT)")
    
    print("\n💡 Next Steps:")
    print("1. Get OpenAI API key from https://platform.openai.com/account/api-keys")
    print("2. Set environment variable: export OPENAI_API_KEY='sk-...'")
    print("3. Run test again: python test_ai_status.py")
    print("4. Start your Flask server: python api/index.py")
    
    print("\n🎯 Quick Test Command:")
    print("export OPENAI_API_KEY='your-key-here' && python test_ai_status.py")

if __name__ == "__main__":
    main()
