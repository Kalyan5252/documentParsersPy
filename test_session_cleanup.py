#!/usr/bin/env python3
"""
Test session cleanup and persistence functionality
"""
import requests
import time
import json

def test_session_cleanup_and_persistence():
    """Test session cleanup mechanisms"""
    print("🧹 Testing Session Cleanup and Persistence")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # Create multiple test sessions
    sessions = []
    for i in range(3):
        session_id = f"cleanup-test-{i}"
        sessions.append(session_id)
        headers = {"X-Session-ID": session_id}
        
        # Create session by accessing memory endpoint
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        print(f"   Created session {i+1}: {session_id}")
    
    print(f"\n📊 Created {len(sessions)} test sessions")
    
    # Test 1: Verify all sessions exist
    print("\n1. Verifying all sessions exist...")
    active_sessions = 0
    for session_id in sessions:
        headers = {"X-Session-ID": session_id}
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            active_sessions += 1
    
    print(f"   ✅ Active sessions: {active_sessions}/{len(sessions)}")
    
    # Test 2: Test cleanup with very short max_age
    print("\n2. Testing cleanup with short max_age (0.001 hours)...")
    
    # Wait a moment to ensure some time passes
    time.sleep(2)
    
    cleanup_response = requests.post(f"{base_url}/session/cleanup", 
                                   json={"max_age_hours": 0.001})
    
    if cleanup_response.status_code == 200:
        result = cleanup_response.json()
        cleaned_count = result.get('cleaned_sessions', 0)
        print(f"   🧹 Sessions cleaned: {cleaned_count}")
    else:
        print(f"   ❌ Cleanup failed: {cleanup_response.text}")
    
    # Test 3: Verify sessions after cleanup
    print("\n3. Verifying sessions after cleanup...")
    remaining_sessions = 0
    for session_id in sessions:
        headers = {"X-Session-ID": session_id}
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 200:
            remaining_sessions += 1
        elif response.status_code == 404:
            print(f"   🗑️  Session {session_id} was cleaned up")
    
    print(f"   📊 Remaining sessions: {remaining_sessions}/{len(sessions)}")
    
    # Test 4: Test cleanup with longer max_age
    print("\n4. Testing cleanup with longer max_age (24 hours)...")
    
    # Create a new session
    new_session_id = "persistent-test-session"
    headers = {"X-Session-ID": new_session_id}
    response = requests.get(f"{base_url}/session/memory", headers=headers)
    print(f"   ✅ Created persistent session: {new_session_id}")
    
    # Cleanup with 24 hour max_age (should not clean recent sessions)
    cleanup_response = requests.post(f"{base_url}/session/cleanup", 
                                   json={"max_age_hours": 24})
    
    if cleanup_response.status_code == 200:
        result = cleanup_response.json()
        cleaned_count = result.get('cleaned_sessions', 0)
        print(f"   🧹 Sessions cleaned with 24h max_age: {cleaned_count}")
    
    # Verify persistent session still exists
    response = requests.get(f"{base_url}/session/memory", headers=headers)
    if response.status_code == 200:
        print(f"   ✅ Persistent session survived 24h cleanup")
    else:
        print(f"   ❌ Persistent session was unexpectedly cleaned")
    
    # Test 5: Test default cleanup (no parameters)
    print("\n5. Testing default cleanup parameters...")
    
    cleanup_response = requests.post(f"{base_url}/session/cleanup")
    if cleanup_response.status_code == 200:
        result = cleanup_response.json()
        cleaned_count = result.get('cleaned_sessions', 0)
        print(f"   🧹 Default cleanup cleaned: {cleaned_count} sessions")
    else:
        print(f"   ❌ Default cleanup failed: {cleanup_response.text}")
    
    # Test 6: Session activity updates
    print("\n6. Testing session activity updates...")
    
    activity_session = "activity-test-session"
    activity_headers = {"X-Session-ID": activity_session}
    
    # Create session
    requests.get(f"{base_url}/session/memory", headers=activity_headers)
    
    # Get initial timestamp
    response = requests.get(f"{base_url}/session/history", headers=activity_headers)
    if response.status_code == 200:
        initial_activity = response.json().get('last_activity')
        print(f"   📅 Initial activity: {initial_activity}")
        
        # Wait and make another request
        time.sleep(1)
        requests.get(f"{base_url}/session/memory", headers=activity_headers)
        
        # Check if activity was updated
        response = requests.get(f"{base_url}/session/history", headers=activity_headers)
        if response.status_code == 200:
            updated_activity = response.json().get('last_activity')
            print(f"   📅 Updated activity: {updated_activity}")
            
            if updated_activity != initial_activity:
                print(f"   ✅ Session activity correctly updated")
            else:
                print(f"   ⚠️  Session activity not updated (might be too fast)")
    
    print("\n" + "=" * 50)
    print("🎉 Session Cleanup and Persistence Testing Complete!")

if __name__ == "__main__":
    test_session_cleanup_and_persistence()
