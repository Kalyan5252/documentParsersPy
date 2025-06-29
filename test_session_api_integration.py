#!/usr/bin/env python3
"""
Test session management with actual file upload
"""
import requests
import pandas as pd
import tempfile
import os
import time

def create_test_excel_file():
    """Create a test Excel file with CDR data"""
    data = {
        'A_PARTY': ['123456789', '987654321', '555666777'],
        'B_PARTY': ['987654321', '123456789', '111222333'],
        'CALL_TYPE': ['OUTGOING', 'INCOMING', 'OUTGOING'],
        'IMEI_A': ['123456789012345', '987654321098765', '555666777888999'],
        'IMSI_A': ['123456789012345', '987654321098765', '555666777888999'],
        'DATE': ['2025-06-29', '2025-06-29', '2025-06-29'],
        'TIME': ['10:30:00', '11:45:00', '14:20:00'],
        'DURATION': ['120', '85', '200']
    }
    
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def test_session_api_integration():
    """Test complete session management with file upload"""
    print("🧪 Testing Session Management API Integration")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    session_id = "integration-test-session"
    headers = {"X-Session-ID": session_id}
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/check")
        print(f"   ✅ API Status: {response.json()['success']}")
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return
    
    # Test 2: Create test file and upload
    print("\n2. Creating and uploading test file...")
    test_file_path = create_test_excel_file()
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_cdr.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ File uploaded successfully")
            print(f"   📄 File type: {result.get('file_type')}")
            print(f"   📊 Records: {result.get('record_count')}")
            print(f"   🔑 Session ID: {result.get('session_id')}")
        else:
            print(f"   ❌ Upload failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return
    finally:
        # Cleanup test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
    
    # Test 3: Check session history
    print("\n3. Checking session history...")
    try:
        response = requests.get(f"{base_url}/session/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Session history retrieved")
            print(f"   📂 Files processed: {len(history.get('file_history', []))}")
            print(f"   💬 Conversation messages: {len(history.get('conversation', []))}")
            print(f"   🕒 Session created: {history.get('created_at')}")
        else:
            print(f"   ❌ History error: {response.text}")
    except Exception as e:
        print(f"   ❌ History error: {e}")
    
    # Test 4: Check session memory
    print("\n4. Checking session memory...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            memory = response.json()
            print(f"   ✅ Session memory retrieved")
            print(f"   🧠 Memory type: {memory.get('memory_type')}")
            print(f"   📝 Message count: {memory.get('message_count')}")
            
            # Print conversation
            for i, msg in enumerate(memory.get('messages', [])[:4], 1):
                msg_type = "👤" if msg['type'] == 'human' else "🤖"
                content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"      {i}. {msg_type} {content}")
        else:
            print(f"   ❌ Memory error: {response.text}")
    except Exception as e:
        print(f"   ❌ Memory error: {e}")
    
    # Test 5: Check session statistics
    print("\n5. Checking session statistics...")
    try:
        response = requests.get(f"{base_url}/session/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Session statistics retrieved")
            print(f"   📊 Files processed: {stats.get('files_processed')}")
            print(f"   📈 File types: {stats.get('file_types')}")
            print(f"   📋 Total records: {stats.get('total_records')}")
            print(f"   ⏱️  Session duration: {stats.get('session_duration'):.1f}s")
        else:
            print(f"   ❌ Stats error: {response.text}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test 6: Test session cleanup
    print("\n6. Testing session cleanup...")
    try:
        response = requests.post(f"{base_url}/session/cleanup", 
                               json={"max_age_hours": 0.001})  # Very short age to test cleanup
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Cleanup completed")
            print(f"   🧹 Sessions cleaned: {result.get('cleaned_sessions', 0)}")
        else:
            print(f"   ❌ Cleanup error: {response.text}")
    except Exception as e:
        print(f"   ❌ Cleanup error: {e}")
    
    # Test 7: Verify session still exists (should exist since we just used it)
    print("\n7. Verifying session persistence...")
    try:
        response = requests.get(f"{base_url}/session/history", headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Session still active after cleanup")
        else:
            print(f"   ℹ️  Session cleaned up (expected with short max_age)")
    except Exception as e:
        print(f"   ❌ Persistence test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Session Management API Integration Test Complete!")

if __name__ == "__main__":
    test_session_api_integration()
