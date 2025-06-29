#!/usr/bin/env python3
"""
Test GitHub Copilot API Integration with Session Management
"""
import requests
import pandas as pd
import tempfile
import os
import json

def create_test_cdr_file():
    """Create a test CDR file"""
    data = {
        'A_PARTY': ['555-1001', '555-1002', '555-1003'],
        'B_PARTY': ['555-2001', '555-2002', '555-2003'],
        'CALL_TYPE': ['OUTGOING', 'INCOMING', 'OUTGOING'],
        'IMEI_A': ['123456789012345', '234567890123456', '345678901234567'],
        'IMSI_A': ['123456789012345', '234567890123456', '345678901234567'],
        'DATE': ['2025-06-29', '2025-06-29', '2025-06-29'],
        'TIME': ['09:15:00', '14:30:00', '18:45:00'],
        'DURATION': ['180', '240', '90']
    }
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def test_copilot_integration():
    """Test GitHub Copilot integration with session management"""
    print("🤖 Testing GitHub Copilot API Integration")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    session_id = "copilot-test-session"
    headers = {"X-Session-ID": session_id}
    
    # Test 1: Check API health
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/check")
        if response.status_code == 200:
            print("   ✅ API is healthy")
        else:
            print("   ❌ API health check failed")
            return
    except Exception as e:
        print(f"   ❌ API connection error: {e}")
        return
    
    # Test 2: Upload file with AI explanation
    print("\n2. Testing file upload with AI explanation...")
    cdr_file = create_test_cdr_file()
    try:
        with open(cdr_file, 'rb') as f:
            files = {'file': ('copilot_test_cdr.xlsx', f)}
            response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ File processed: {result.get('file_type')}")
            print(f"   📊 Records: {result.get('record_count')}")
            
            # Check if AI explanation was generated
            ai_explanation = result.get('ai_explanation', '')
            if ai_explanation and 'unavailable' not in ai_explanation.lower():
                print(f"   🤖 AI Explanation: {ai_explanation[:100]}...")
            else:
                print(f"   ⚠️  AI Explanation: {ai_explanation}")
        else:
            print(f"   ❌ File upload failed: {response.text}")
            return
    finally:
        os.unlink(cdr_file)
    
    # Test 3: Get AI analysis of session
    print("\n3. Testing AI session analysis...")
    try:
        response = requests.get(f"{base_url}/session/ai/analysis", headers=headers)
        if response.status_code == 200:
            analysis = response.json()
            if 'analysis' in analysis:
                print(f"   ✅ AI Analysis generated")
                print(f"   📝 Analysis: {analysis['analysis'][:150]}...")
            else:
                print(f"   ⚠️  Analysis error: {analysis.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Analysis request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
    
    # Test 4: Ask AI a question
    print("\n4. Testing AI question answering...")
    question = "What patterns do you see in the call data I uploaded?"
    try:
        response = requests.post(f"{base_url}/session/ai/ask", 
                               headers=headers,
                               json={"question": question})
        
        if response.status_code == 200:
            result = response.json()
            if 'answer' in result:
                print(f"   ✅ AI answered question")
                print(f"   ❓ Question: {question}")
                print(f"   🤖 Answer: {result['answer'][:150]}...")
            else:
                print(f"   ⚠️  Answer error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Question request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Question error: {e}")
    
    # Test 5: Get AI suggestions
    print("\n5. Testing AI suggestions...")
    try:
        response = requests.get(f"{base_url}/session/ai/suggestions", headers=headers)
        if response.status_code == 200:
            suggestions = response.json()
            if 'suggestions' in suggestions:
                print(f"   ✅ AI suggestions generated")
                print("   💡 Suggestions:")
                for i, suggestion in enumerate(suggestions['suggestions'][:3], 1):
                    print(f"      {i}. {suggestion}")
            else:
                print(f"   ⚠️  Suggestions error: {suggestions.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Suggestions request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Suggestions error: {e}")
    
    # Test 6: Test AI chat functionality
    print("\n6. Testing AI chat...")
    chat_message = "How can I analyze call patterns for suspicious activity?"
    try:
        response = requests.post(f"{base_url}/session/ai/chat",
                               headers=headers,
                               json={"message": chat_message})
        
        if response.status_code == 200:
            chat_result = response.json()
            if 'response' in chat_result:
                print(f"   ✅ AI chat working")
                print(f"   💬 Message: {chat_message}")
                print(f"   🤖 Response: {chat_result['response'][:150]}...")
            else:
                print(f"   ⚠️  Chat error: {chat_result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Chat request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
    
    # Test 7: Check conversation memory with AI interactions
    print("\n7. Testing conversation memory with AI...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            memory = response.json()
            messages = memory.get('messages', [])
            ai_messages = [msg for msg in messages if msg['type'] == 'ai']
            
            print(f"   ✅ Memory contains {len(messages)} total messages")
            print(f"   🤖 AI messages: {len(ai_messages)}")
            
            # Show recent AI interactions
            if ai_messages:
                print("   📝 Recent AI interactions:")
                for i, msg in enumerate(ai_messages[-2:], 1):
                    content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
                    print(f"      {i}. {content}")
        else:
            print(f"   ❌ Memory check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Memory error: {e}")
    
    # Test 8: File type explanation
    print("\n8. Testing file type explanation...")
    try:
        columns = ['A_PARTY', 'B_PARTY', 'CALL_TYPE', 'IMEI_A', 'IMSI_A']
        params = '&'.join([f'columns={col}' for col in columns])
        response = requests.get(f"{base_url}/session/ai/explain/CDR?{params}", headers=headers)
        
        if response.status_code == 200:
            explanation = response.json()
            if 'explanation' in explanation:
                print(f"   ✅ File type explanation generated")
                print(f"   📚 CDR Explanation: {explanation['explanation'][:150]}...")
            else:
                print(f"   ⚠️  Explanation error: {explanation.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Explanation request failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Explanation error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 GitHub Copilot Integration Test Summary")
    print("=" * 60)
    print("🔑 Session ID:", session_id)
    print("🤖 AI Features Tested:")
    print("   • File type explanations during upload")
    print("   • Session data analysis")
    print("   • Question answering")
    print("   • Action suggestions")
    print("   • General chat capabilities")
    print("   • Conversation memory integration")
    print("\n🎉 GitHub Copilot Integration Test Complete!")

if __name__ == "__main__":
    test_copilot_integration()
