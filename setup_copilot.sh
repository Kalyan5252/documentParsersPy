#!/bin/bash
# GitHub Copilot API Setup Script

echo "🤖 GitHub Copilot API Setup"
echo "=========================="

# Check if API key is already set
if [ -n "$GITHUB_COPILOT_API_KEY" ]; then
    echo "✅ GITHUB_COPILOT_API_KEY is already set"
    echo "   Key preview: ${GITHUB_COPILOT_API_KEY:0:8}..."
else
    echo "❌ GITHUB_COPILOT_API_KEY is not set"
    echo ""
    echo "To set your GitHub Copilot API key, run:"
    echo "export GITHUB_COPILOT_API_KEY='your_api_key_here'"
    echo ""
    echo "Or add it to your .env file:"
    echo "echo 'GITHUB_COPILOT_API_KEY=your_api_key_here' >> .env"
fi

echo ""
echo "📝 How to get your GitHub Copilot API key:"
echo "1. Go to https://github.com/features/copilot"
echo "2. Sign up for GitHub Copilot if you haven't already"
echo "3. Contact GitHub support for API access or check your GitHub Enterprise settings"
echo "4. For GitHub Enterprise users, check with your admin for API access"

echo ""
echo "🚀 After setting the API key, restart your Flask server:"
echo "python api/index.py"

echo ""
echo "🧪 Test the integration with:"
echo "python test_github_copilot_api.py"
