# Session Memory with LangChain Integration

## Overview

This implementation adds **LangChain ConversationBufferMemory** to the documentParsersPy project, enabling persistent session management and conversation tracking across file uploads and processing.

## Architecture

### Session Management Components

1. **SessionManager Class** (`api/session_manager.py`)
   - Manages user sessions with UUID-based session IDs
   - Integrates LangChain `ConversationBufferMemory` for conversation tracking
   - Stores file processing history and processing context
   - Provides session cleanup and statistics

2. **Flask Integration** (`api/index.py`)
   - Session-aware endpoints with `X-Session-ID` header support
   - Automatic session creation and management
   - Session data included in API responses

3. **Memory Types Used**
   - `ConversationBufferMemory`: Stores complete conversation history
   - Custom session storage: File history, processing context, timestamps

## Session Data Structure

```python
{
    'memory': ConversationBufferMemory(return_messages=True),
    'created_at': datetime.now(),
    'last_activity': datetime.now(),
    'file_history': [
        {
            'filename': 'data.xlsx',
            'file_type': 'CDR',
            'processed_at': '2025-06-29T...',
            'status': 'success',
            'record_count': 1500,
            'columns': ['A_PARTY', 'B_PARTY', ...]
        }
    ],
    'processing_context': {
        'last_file_type': 'CDR',
        'total_files_processed': 3,
        'custom_analysis_data': '...'
    }
}
```

## API Endpoints

### File Processing (Enhanced)
```http
POST /parse-data
Headers: X-Session-ID: your-session-id
Content-Type: multipart/form-data

Body: file=your_file.xlsx
```

**Response includes session data:**
```json
{
    "status": "success",
    "file_type": "CDR", 
    "session_id": "uuid-here",
    "record_count": 1500,
    "columns": ["A_PARTY", "B_PARTY", ...]
}
```

### Session Management

#### Get Session History
```http
GET /session/history
Headers: X-Session-ID: your-session-id
```

#### Get Session Statistics  
```http
GET /session/stats
Headers: X-Session-ID: your-session-id
```

#### Get Conversation Memory
```http
GET /session/memory
Headers: X-Session-ID: your-session-id
```

#### Cleanup Old Sessions
```http
POST /session/cleanup
Content-Type: application/json

{"max_age_hours": 24}
```

## Usage Examples

### 1. File Upload with Session Tracking
```python
import requests

session_id = "my-analysis-session"
headers = {"X-Session-ID": session_id}

# Upload file
with open("cdr_data.xlsx", "rb") as f:
    response = requests.post(
        "http://localhost:5000/parse-data",
        files={"file": f},
        headers=headers
    )

print(f"File processed: {response.json()}")
```

### 2. Retrieve Session History
```python
# Get session history
response = requests.get(
    "http://localhost:5000/session/history",
    headers=headers
)

history = response.json()
print(f"Files processed: {len(history['file_history'])}")
print(f"Conversations: {len(history['conversation'])}")
```

### 3. Access Conversation Memory
```python
# Get conversation memory
response = requests.get(
    "http://localhost:5000/session/memory", 
    headers=headers
)

memory = response.json()
for msg in memory['messages']:
    print(f"{msg['type']}: {msg['content']}")
```

## Memory Benefits

### 1. **Conversation Continuity**
- Track user interactions across multiple API calls
- Maintain context of file processing history
- Enable conversational AI features

### 2. **Processing Analytics**
- File type distribution per session
- Processing success/failure rates
- Record count summaries

### 3. **Error Tracking** 
- Store error messages in conversation memory
- Track failed processing attempts
- Provide debugging context

### 4. **Session Persistence**
- Sessions persist until cleanup
- Automatic session ID generation
- Cross-request state management

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-flask-secret-key-here
```

### Dependencies Added
```txt
langchain>=0.3.26
langchain-core>=0.3.66
```

## Testing

Run the test script to verify functionality:
```bash
python test_session_memory.py
```

Run the API demo:
```bash
# Terminal 1: Start Flask app
cd api && python index.py

# Terminal 2: Test session endpoints  
python demo_session_api.py
```

## Future Enhancements

1. **Database Persistence**: Store sessions in Redis/PostgreSQL
2. **Advanced Memory Types**: Use `ConversationSummaryMemory` for large sessions
3. **Session Analytics**: Enhanced reporting and visualization
4. **Multi-user Support**: User authentication and isolation
5. **Memory Optimization**: Automatic conversation summarization

## Security Considerations

- Session IDs should be cryptographically secure
- Implement session timeout and cleanup
- Add rate limiting for session creation
- Consider encryption for sensitive conversation data
- Validate session ownership for multi-user environments
