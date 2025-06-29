#!/usr/bin/env python3
"""
Session Management Test Summary
Quick verification that all components are working
"""
import requests
import pandas as pd
import tempfile
import os

def create_simple_cdr():
    """Create a simple CDR test file"""
    data = {
        'A_PARTY': ['555-1234'],
        'B_PARTY': ['555-5678'],
        'CALL_TYPE': ['OUTGOING'],
        'IMEI_A': ['123456789012345'],
        'IMSI_A': ['123456789012345']
    }
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def test_session_summary():
    """Run a comprehensive but quick test of session management"""
    print("🎯 Session Management Test Summary")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    session_id = "final-test-session"
    headers = {"X-Session-ID": session_id}
    
    tests = []
    
    # Test 1: API Health
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/check", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is healthy")
            tests.append(True)
        else:
            print("   ❌ API health check failed")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ API connection error: {e}")
        tests.append(False)
        return
    
    # Test 2: Session Creation
    print("\n2. Testing session creation...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("session_id") == session_id:
                print(f"   ✅ Session created: {session_id}")
                tests.append(True)
            else:
                print("   ❌ Session ID mismatch")
                tests.append(False)
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Session creation error: {e}")
        tests.append(False)
    
    # Test 3: File Upload and Processing
    print("\n3. Testing file upload and processing...")
    cdr_file = create_simple_cdr()
    try:
        with open(cdr_file, 'rb') as f:
            files = {'file': ('summary_test.xlsx', f)}
            response = requests.post(f"{base_url}/parse-data", files=files, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("file_type") == "CDR":
                print(f"   ✅ File processed as {result.get('file_type')} with {result.get('record_count')} records")
                tests.append(True)
            else:
                print(f"   ❌ Unexpected file type: {result.get('file_type')}")
                tests.append(False)
        else:
            print(f"   ❌ File upload failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ File upload error: {e}")
        tests.append(False)
    finally:
        os.unlink(cdr_file)
    
    # Test 4: Memory and Conversation
    print("\n4. Testing conversation memory...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers, timeout=5)
        if response.status_code == 200:
            memory = response.json()
            message_count = memory.get("message_count", 0)
            if message_count >= 2:  # Should have human + AI messages from file upload
                print(f"   ✅ Conversation memory working: {message_count} messages")
                tests.append(True)
            else:
                print(f"   ❌ Not enough messages in memory: {message_count}")
                tests.append(False)
        else:
            print(f"   ❌ Memory check failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Memory check error: {e}")
        tests.append(False)
    
    # Test 5: Session History
    print("\n5. Testing session history...")
    try:
        response = requests.get(f"{base_url}/session/history", headers=headers, timeout=5)
        if response.status_code == 200:
            history = response.json()
            files = len(history.get("file_history", []))
            if files >= 1:
                print(f"   ✅ Session history working: {files} files processed")
                tests.append(True)
            else:
                print(f"   ❌ No files in history")
                tests.append(False)
        else:
            print(f"   ❌ History check failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ History check error: {e}")
        tests.append(False)
    
    # Test 6: Session Statistics
    print("\n6. Testing session statistics...")
    try:
        response = requests.get(f"{base_url}/session/stats", headers=headers, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            if stats.get("files_processed", 0) >= 1:
                print(f"   ✅ Statistics working: {stats.get('files_processed')} files, {stats.get('total_records')} records")
                tests.append(True)
            else:
                print(f"   ❌ No files in statistics")
                tests.append(False)
        else:
            print(f"   ❌ Stats check failed: {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ Stats check error: {e}")
        tests.append(False)
    
    # Summary
    passed = sum(tests)
    total = len(tests)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 PERFECT: All session management features working!")
    elif success_rate >= 80:
        print("✅ EXCELLENT: Session management mostly working!")
    elif success_rate >= 60:
        print("⚠️ GOOD: Session management working with some issues")
    else:
        print("❌ POOR: Major session management issues detected")
    
    print(f"\n🔑 Test Session ID: {session_id}")
    print("🚀 Session Management Test Complete!")

if __name__ == "__main__":
    test_session_summary()
