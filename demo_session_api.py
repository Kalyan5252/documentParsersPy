#!/usr/bin/env python3
"""
API Demo showing session memory endpoints
Run this while the Flask app is running to test the session API endpoints
"""
import requests
import json

def demo_session_api():
    base_url = "http://localhost:5000"
    
    print("🌐 Session Memory API Demo")
    print("=" * 40)
    
    # Test health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/check")
        print(f"   ✅ API Status: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ API not running. Start with: cd api && python index.py")
        return
    
    # Session ID for testing
    session_id = "demo-session-123"
    headers = {"X-Session-ID": session_id}
    
    print(f"\n2. Using session ID: {session_id}")
    
    # Test session memory endpoint
    print("\n3. Getting session memory...")
    try:
        response = requests.get(f"{base_url}/session/memory", headers=headers)
        if response.status_code == 404:
            print("   📝 New session - no memory yet")
        else:
            data = response.json()
            print(f"   💾 Memory messages: {data.get('message_count', 0)}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Test session history
    print("\n4. Getting session history...")
    try:
        response = requests.get(f"{base_url}/session/history", headers=headers)
        if response.status_code == 404:
            print("   📂 New session - no history yet")
        else:
            data = response.json()
            print(f"   📊 Files processed: {len(data.get('file_history', []))}")
            print(f"   💬 Conversations: {len(data.get('conversation', []))}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Test session stats
    print("\n5. Getting session statistics...")
    try:
        response = requests.get(f"{base_url}/session/stats", headers=headers)
        if response.status_code == 404:
            print("   📈 New session - no stats yet")
        else:
            data = response.json()
            print(f"   📊 Stats: {json.dumps(data, indent=6)}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    print("\n" + "=" * 40)
    print("📝 To test file upload with session memory:")
    print(f"   curl -X POST -H 'X-Session-ID: {session_id}' \\")
    print(f"        -F 'file=@your_file.xlsx' \\")
    print(f"        {base_url}/parse-data")
    
    print("\n🚀 Session API Demo Complete!")

if __name__ == "__main__":
    demo_session_api()
