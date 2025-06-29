#!/usr/bin/env python3
"""
Comprehensive Session Management Test Suite
Tests all aspects of the LangChain session memory integration
"""
import requests
import pandas as pd
import tempfile
import os
import time
import json

def create_cdr_file():
    """Create a CDR test file"""
    data = {
        'A_PARTY': ['555-1234', '555-5678'],
        'B_PARTY': ['555-9876', '555-4321'],
        'CALL_TYPE': ['OUTGOING', 'INCOMING'],
        'IMEI_A': ['123456789012345', '987654321098765'],
        'IMSI_A': ['123456789012345', '987654321098765'],
        'DATE': ['2025-06-29', '2025-06-29'],
        'TIME': ['10:00:00', '11:00:00'],
        'DURATION': ['120', '180']
    }
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def create_td_file():
    """Create a Tower Data test file"""
    data = {
        'A_PARTY': ['555-1111', '555-2222'],
        'B_PARTY': ['555-3333', '555-4444'],
        'CALL_TYPE': ['OUTGOING', 'INCOMING'],
        'IMEI_A': ['111222333444555', '666777888999000'],
        'IMSI_A': ['111222333444555', '666777888999000'],
        'ROAMING_A': ['Yes', 'No'],  # This makes it TD instead of CDR
        'FIRST_CELL_ID_A': ['CELL001', 'CELL002'],
        'LAST_CELL_ID_A': ['CELL003', 'CELL004']
    }
    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name

def comprehensive_session_test():
    """Run comprehensive session management tests"""
    print("🎯 Comprehensive Session Management Test Suite")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    main_session_id = "comprehensive-test-session"
    headers = {"X-Session-ID": main_session_id}
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "errors": []
    }
    
    def run_test(test_name, test_func):
        test_results["total_tests"] += 1
        try:
            print(f"\n{test_results['total_tests']}. {test_name}")
            success = test_func()
            if success:
                test_results["passed_tests"] += 1
                print(f"   ✅ PASSED")
            else:
                test_results["failed_tests"] += 1
                print(f"   ❌ FAILED")
        except Exception as e:
            test_results["failed_tests"] += 1
            test_results["errors"].append(f"{test_name}: {str(e)}")
            print(f"   ❌ ERROR: {str(e)}")
    
    # Test 1: Basic API Health
    def test_api_health():
        response = requests.get(f"{base_url}/check")
        return response.status_code == 200 and response.json().get("success") == "working"
    
    # Test 2: Session Creation via Memory Endpoint
    def test_session_creation():
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return (data.get("session_id") == main_session_id and 
                   data.get("memory_type") == "ConversationBufferMemory")
        return False
    
    # Test 3: CDR File Upload
    def test_cdr_upload():
        cdr_file = create_cdr_file()
        try:
            with open(cdr_file, 'rb') as f:
                files = {'file': ('test_cdr.xlsx', f)}
                response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return (result.get("file_type") == "CDR" and 
                       result.get("status") == "success")
            return False
        finally:
            os.unlink(cdr_file)
    
    # Test 4: TD File Upload
    def test_td_upload():
        td_file = create_td_file()
        try:
            with open(td_file, 'rb') as f:
                files = {'file': ('test_td.xlsx', f)}
                response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return (result.get("file_type") == "TD" and 
                       result.get("status") == "success")
            return False
        finally:
            os.unlink(td_file)
    
    # Test 5: Session History Tracking
    def test_session_history():
        response = requests.get(f"{base_url}/session/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            files = history.get("file_history", [])
            conversation = history.get("conversation", [])
            return len(files) >= 2 and len(conversation) >= 4  # At least 2 files, 4 messages
        return False
    
    # Test 6: Memory Content Validation
    def test_memory_content():
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            memory = response.json()
            messages = memory.get("messages", [])
            return len(messages) >= 4  # Should have messages from file uploads
        return False
    
    # Test 7: Session Statistics
    def test_session_stats():
        response = requests.get(f"{base_url}/session/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            file_types = stats.get("file_types", {})
            return ("CDR" in file_types and "TD" in file_types and 
                   stats.get("files_processed", 0) >= 2)
        return False
    
    # Test 8: Error Handling
    def test_error_handling():
        # Create invalid file
        invalid_data = {"INVALID": ["data1"], "COLUMNS": ["data2"]}
        df = pd.DataFrame(invalid_data)
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('invalid.xlsx', f)}
                response = requests.post(f"{base_url}/parse-data", files=files, headers=headers)
            
            # Should return error but still track in session
            if response.status_code == 400:
                # Check if error was logged in session
                mem_response = requests.get(f"{base_url}/session/memory", headers=headers)
                if mem_response.status_code == 200:
                    messages = mem_response.json().get("messages", [])
                    error_messages = [msg for msg in messages if "Error" in msg.get("content", "")]
                    return len(error_messages) > 0
            return False
        finally:
            os.unlink(temp_file.name)
    
    # Test 9: Session Persistence Across Requests
    def test_session_persistence():
        # Make multiple requests and verify session data persists
        for i in range(3):
            response = requests.get(f"{base_url}/session/memory", headers=headers)
            if response.status_code != 200:
                return False
        
        # Verify session history still exists
        response = requests.get(f"{base_url}/session/history", headers=headers)
        return response.status_code == 200
    
    # Test 10: Auto Session Creation
    def test_auto_session():
        # Upload file without session header
        cdr_file = create_cdr_file()
        try:
            with open(cdr_file, 'rb') as f:
                files = {'file': ('auto_test.xlsx', f)}
                response = requests.post(f"{base_url}/parse-data", files=files)
            
            if response.status_code == 200:
                result = response.json()
                auto_session_id = result.get("session_id")
                if auto_session_id:
                    # Verify the auto-created session exists
                    auto_headers = {"X-Session-ID": auto_session_id}
                    hist_response = requests.get(f"{base_url}/session/history", headers=auto_headers)
                    return hist_response.status_code == 200
            return False
        finally:
            os.unlink(cdr_file)
    
    # Run all tests
    run_test("API Health Check", test_api_health)
    run_test("Session Creation via Memory Endpoint", test_session_creation)
    run_test("CDR File Upload and Processing", test_cdr_upload)
    run_test("TD File Upload and Processing", test_td_upload)
    run_test("Session History Tracking", test_session_history)
    run_test("Memory Content Validation", test_memory_content)
    run_test("Session Statistics Generation", test_session_stats)
    run_test("Error Handling and Logging", test_error_handling)
    run_test("Session Persistence Across Requests", test_session_persistence)
    run_test("Automatic Session Creation", test_auto_session)
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed_tests']}")
    print(f"❌ Failed: {test_results['failed_tests']}")
    
    if test_results['errors']:
        print("\n🚨 ERRORS:")
        for error in test_results['errors']:
            print(f"   - {error}")
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Session management is working perfectly!")
    elif success_rate >= 70:
        print("✅ GOOD: Session management is working well with minor issues")
    else:
        print("⚠️ NEEDS ATTENTION: Several session management issues detected")
    
    print(f"\n🔑 Main Test Session ID: {main_session_id}")
    print("🌟 Session Memory Integration Test Complete!")

if __name__ == "__main__":
    comprehensive_session_test()
