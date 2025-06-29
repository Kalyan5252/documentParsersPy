# GitHub Copilot API Integration Setup

## Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# GitHub Copilot API (from GitHub Enterprise or Copilot Chat API)
GITHUB_COPILOT_API_KEY=your_github_copilot_api_key_here

# Flask Configuration  
SECRET_KEY=your-secret-key-for-sessions-2024

# Neo4j Configuration (existing)
NEO4J_URI=neo4j+s://0d71a2dd.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASS=bJMtMTV6eZNNxYeRN6D4N4s5cspQLou0qTt2qjzjD40
```

## Setting Up GitHub Copilot API Key

1. **Get your GitHub Copilot API key** from GitHub's developer console or through GitHub Enterprise
   - For GitHub Copilot Enterprise: Contact your GitHub Enterprise admin
   - For GitHub Copilot API access: Visit https://github.com/features/copilot
2. **Set the environment variable**:
   ```bash
   export GITHUB_COPILOT_API_KEY="your_api_key_here"
   ```
   Or add it to your `.env` file

**Note:** The GitHub Copilot API uses a different authentication mechanism than OpenAI. Make sure you have the correct API key from GitHub.

## Installation

Install the updated dependencies:
```bash
pip install -r requirements.txt
```

## New AI-Powered Endpoints

### 1. AI Session Analysis
```http
GET /session/ai/analysis
Headers: X-Session-ID: your-session-id
```
**Response:**
```json
{
    "analysis": "Your session shows processing of CDR data with 1500 call records...",
    "timestamp": "2025-06-29T10:30:00"
}
```

### 2. AI Question Answering
```http
POST /session/ai/ask
Headers: X-Session-ID: your-session-id
Content-Type: application/json

{
    "question": "What patterns do you see in my call data?"
}
```

### 3. AI Action Suggestions
```http
GET /session/ai/suggestions
Headers: X-Session-ID: your-session-id
```

### 4. AI Chat Interface
```http
POST /session/ai/chat
Headers: X-Session-ID: your-session-id
Content-Type: application/json

{
    "message": "How can I identify suspicious call patterns?"
}
```

### 5. File Type Explanations
```http
GET /session/ai/explain/CDR?columns=A_PARTY&columns=B_PARTY&columns=CALL_TYPE
Headers: X-Session-ID: your-session-id
```

## Enhanced File Processing

File uploads now automatically include AI explanations:

```json
{
    "status": "success",
    "file_type": "CDR", 
    "session_id": "uuid-here",
    "record_count": 1500,
    "columns": ["A_PARTY", "B_PARTY", ...],
    "ai_explanation": "CDR (Call Detail Records) files contain telecommunications data..."
}
```

## Testing

Run the comprehensive test:
```bash
python test_copilot_integration.py
```

## Usage Examples

### Python Client Example
```python
import requests

session_id = "my-analysis-session"
headers = {"X-Session-ID": session_id}

# Upload file with AI explanation
with open("cdr_data.xlsx", "rb") as f:
    response = requests.post(
        "http://localhost:5000/parse-data",
        files={"file": f},
        headers=headers
    )
    result = response.json()
    print(f"AI Explanation: {result['ai_explanation']}")

# Ask AI a question
response = requests.post(
    "http://localhost:5000/session/ai/ask",
    headers=headers,
    json={"question": "What insights can you provide about this data?"}
)
answer = response.json()
print(f"AI Answer: {answer['answer']}")

# Get AI suggestions
response = requests.get(
    "http://localhost:5000/session/ai/suggestions",
    headers=headers
)
suggestions = response.json()
for suggestion in suggestions['suggestions']:
    print(f"• {suggestion}")
```

### cURL Examples
```bash
# Get AI analysis
curl -H "X-Session-ID: my-session" \
     http://localhost:5000/session/ai/analysis

# Ask a question
curl -X POST \
     -H "X-Session-ID: my-session" \
     -H "Content-Type: application/json" \
     -d '{"question": "What patterns do you see?"}' \
     http://localhost:5000/session/ai/ask

# Get suggestions
curl -H "X-Session-ID: my-session" \
     http://localhost:5000/session/ai/suggestions
```

## AI Capabilities

The GitHub Copilot integration provides:

1. **Intelligent File Analysis**
   - Automatic explanation of uploaded file types
   - Pattern recognition in telecommunications data
   - Statistical insights and trends

2. **Conversational Interface**
   - Natural language question answering
   - Context-aware responses based on session history
   - Technical guidance for data analysis

3. **Action Recommendations**
   - Suggested next steps for investigation
   - Analysis techniques recommendations
   - Data exploration guidance

4. **Domain Expertise**
   - Telecommunications data format knowledge
   - Call pattern analysis insights
   - Security and investigative perspectives

## Error Handling

If GitHub Copilot API is not available:
- Endpoints return `{"error": "GitHub Copilot API not available"}`
- File uploads still work but without AI explanations
- Session management continues normally

## Security Considerations

- API keys should be kept secure and not committed to version control
- Consider rate limiting for AI endpoints
- Session data with AI responses should be handled according to data privacy requirements
- Review AI responses for sensitive information before logging
