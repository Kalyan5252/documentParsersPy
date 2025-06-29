#!/usr/bin/env python3
"""
Advanced session management testing - Multiple files and error scenarios
"""
import requests
import pandas as pd
import tempfile
import os
import time

def create_ipdr_test_file():
    """Create a test IPDR Excel file"""
    data = {
        'LANDLINE/MSISDN/MDN/LEASED_CIRCUIT_ID_FOR_INTERNET_ACCESS': ['123456789', '987654321'],
        'SOURCE_IP_ADDRESS': ['192.168.1.100', '10.0.0.50'],
        'TRANSLATED_IP_ADDRESS': ['203.0.113.1', '198.51.100.2'],
        'DESTINATION_IP_ADDRESS': ['8.8.8.8', '1.1.1.1'],
        'SESSION_DURATION': ['300', '450'],
        'DATA_VOLUME_UP_LINK': ['1024', '2048'],
        'DATA_VOLUME_DOWN_LINK': ['5120', '8192']
    }
    
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def create_invalid_file():
    """Create an invalid Excel file (unknown type)"""
    data = {
        'Random_Column_1': ['data1', 'data2'],
        'Random_Column_2': ['data3', 'data4'],
        'Unknown_Format': ['test', 'test2']
    }
    
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def test_advanced_session_scenarios():
    """Test advanced session management scenarios"""
    print("🔬 Advanced Session Management Testing")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    session_id = "advanced-test-session"
    headers = {"X-Session-ID": session_id}
    
    # Test 1: Upload multiple files of different types
    print("\n1. Testing multiple file uploads...")
    
    # Upload IPDR file
    ipdr_file = create_ipdr_test_file()
    try:
        with open(ipdr_file, 'rb') as f:
            files = {'file': ('test_ipdr.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ IPDR file uploaded: {result.get('file_type')} with {result.get('record_count')} records")
        else:
            print(f"   ❌ IPDR upload failed: {response.text}")
    finally:
        os.unlink(ipdr_file)
    
    # Upload invalid file (should trigger error)
    print("\n2. Testing error handling with invalid file...")
    invalid_file = create_invalid_file()
    try:
        with open(invalid_file, 'rb') as f:
            files = {'file': ('invalid_file.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
        
        if response.status_code == 400:
            result = response.json()
            print(f"   ✅ Error handled correctly: {result.get('error')}")
            print(f"   📊 Detected columns: {result.get('detected_columns')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    finally:
        os.unlink(invalid_file)
    
    # Test 3: Check comprehensive session history
    print("\n3. Checking comprehensive session history...")
    try:
        response = requests.get(f"{base_url}/session/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Complete session history:")
            print(f"   📂 Total files processed: {len(history.get('file_history', []))}")
            
            # Show file history details
            for i, file_info in enumerate(history.get('file_history', []), 1):
                print(f"      {i}. {file_info.get('filename')} ({file_info.get('file_type')}) - {file_info.get('status')}")
            
            # Show conversation including errors
            conversation = history.get('conversation', [])
            print(f"   💬 Total conversation messages: {len(conversation)}")
            
            for i, msg in enumerate(conversation, 1):
                msg_type = "👤" if msg['type'] == 'human' else "🤖"
                content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
                print(f"      {i}. {msg_type} {content}")
        else:
            print(f"   ❌ History error: {response.text}")
    except Exception as e:
        print(f"   ❌ History error: {e}")
    
    # Test 4: Session statistics with mixed results
    print("\n4. Checking session statistics with mixed results...")
    try:
        response = requests.get(f"{base_url}/session/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Mixed session statistics:")
            print(f"   📊 Files processed: {stats.get('files_processed')}")
            print(f"   📈 File types breakdown: {stats.get('file_types')}")
            print(f"   📋 Total records processed: {stats.get('total_records')}")
            print(f"   💬 Conversation messages: {stats.get('conversation_messages')}")
        else:
            print(f"   ❌ Stats error: {response.text}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test 5: Test session without header (should create new session)
    print("\n5. Testing automatic session creation...")
    try:
        # Upload without session header
        ipdr_file2 = create_ipdr_test_file()
        with open(ipdr_file2, 'rb') as f:
            files = {'file': ('auto_session_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/parse-data", files=files)
        
        if response.status_code == 200:
            result = response.json()
            auto_session_id = result.get('session_id')
            print(f"   ✅ Auto session created: {auto_session_id}")
            print(f"   📄 File processed: {result.get('file_type')}")
            
            # Check the auto-created session
            auto_headers = {"X-Session-ID": auto_session_id}
            hist_response = requests.get(f"{base_url}/session/history", headers=auto_headers)
            if hist_response.status_code == 200:
                auto_history = hist_response.json()
                print(f"   📊 Auto session has {len(auto_history.get('file_history', []))} files")
        else:
            print(f"   ❌ Auto session test failed: {response.text}")
        
        os.unlink(ipdr_file2)
    except Exception as e:
        print(f"   ❌ Auto session error: {e}")
    
    # Test 6: Test memory content validation
    print("\n6. Validating memory content structure...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            memory = response.json()
            print(f"   ✅ Memory structure validation:")
            print(f"   🧠 Session ID present: {'session_id' in memory}")
            print(f"   📝 Message count: {memory.get('message_count')}")
            print(f"   🔄 Memory type: {memory.get('memory_type')}")
            
            # Validate message structure
            messages = memory.get('messages', [])
            human_msgs = sum(1 for msg in messages if msg['type'] == 'human')
            ai_msgs = sum(1 for msg in messages if msg['type'] == 'ai')
            print(f"   👤 Human messages: {human_msgs}")
            print(f"   🤖 AI messages: {ai_msgs}")
        else:
            print(f"   ❌ Memory validation error: {response.text}")
    except Exception as e:
        print(f"   ❌ Memory validation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Advanced Session Management Testing Complete!")
    print(f"🔑 Main session ID: {session_id}")

if __name__ == "__main__":
    test_advanced_session_scenarios()
