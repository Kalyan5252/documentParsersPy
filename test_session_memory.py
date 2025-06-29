#!/usr/bin/env python3
"""
Test script to demonstrate LangChain session memory functionality
"""
import sys
import os
sys.path.append('/workspaces/documentParsersPy/api')

from session_manager import session_manager
import json

def test_session_memory():
    print("🧪 Testing LangChain Session Memory Integration")
    print("=" * 50)
    
    # Test 1: Create a new session
    print("\n1. Creating new session...")
    session_id, session_data = session_manager.get_or_create_session()
    print(f"   ✅ Session created: {session_id}")
    print(f"   📊 Memory type: {type(session_data['memory']).__name__}")
    
    # Test 2: Add file processing to session
    print("\n2. Adding file processing to session...")
    file_info = {
        'filename': 'test_cdr_data.xlsx',
        'file_type': 'CDR',
        'record_count': 1500,
        'status': 'success',
        'columns': ['A_PARTY', 'B_PARTY', 'CALL_TYPE', 'IMEI_A', 'IMSI_A']
    }
    session_manager.add_file_to_session(session_id, file_info)
    print("   ✅ File processing added to session memory")
    
    # Test 3: Add another file
    print("\n3. Adding second file...")
    file_info2 = {
        'filename': 'test_ipdr_data.xlsx',
        'file_type': 'IPDR',
        'record_count': 2300,
        'status': 'success',
        'columns': ['SOURCE_IP_ADDRESS', 'DESTINATION_IP_ADDRESS', 'SESSION_DURATION']
    }
    session_manager.add_file_to_session(session_id, file_info2)
    print("   ✅ Second file processing added to session memory")
    
    # Test 4: Add error to session
    print("\n4. Adding error scenario...")
    session_manager.add_error_to_session(session_id, "corrupted_file.xlsx", "File format not recognized")
    print("   ✅ Error added to session memory")
    
    # Test 5: Get conversation memory
    print("\n5. Retrieving conversation memory...")
    memory_data = session_data['memory']
    messages = memory_data.chat_memory.messages
    print(f"   📝 Total messages in memory: {len(messages)}")
    
    for i, message in enumerate(messages, 1):
        msg_type = "👤 Human" if 'Human' in str(type(message)) else "🤖 AI"
        content_preview = message.content[:60] + "..." if len(message.content) > 60 else message.content
        print(f"      {i}. {msg_type}: {content_preview}")
    
    # Test 6: Get session history
    print("\n6. Getting session history...")
    history = session_manager.get_session_history(session_id)
    print(f"   📂 Files processed: {len(history['file_history'])}")
    print(f"   💬 Conversation messages: {len(history['conversation'])}")
    
    # Test 7: Get session statistics
    print("\n7. Getting session statistics...")
    stats = session_manager.get_session_stats(session_id)
    print(f"   📊 Statistics:")
    print(f"      - Files processed: {stats['files_processed']}")
    print(f"      - File types: {stats['file_types']}")
    print(f"      - Total records: {stats['total_records']}")
    print(f"      - Conversation messages: {stats['conversation_messages']}")
    
    # Test 8: Update processing context
    print("\n8. Testing processing context...")
    session_manager.update_processing_context(session_id, {
        'last_analysis': 'Call pattern analysis completed',
        'total_calls_analyzed': 3800,
        'suspicious_patterns_found': 5
    })
    print("   ✅ Processing context updated")
    
    # Test 9: Memory persistence
    print("\n9. Testing memory persistence...")
    same_session_id, same_session_data = session_manager.get_or_create_session(session_id)
    print(f"   ✅ Session retrieved: {same_session_id == session_id}")
    print(f"   💾 Memory preserved: {len(same_session_data['memory'].chat_memory.messages)} messages")
    
    print("\n" + "=" * 50)
    print("🎉 All session memory tests completed successfully!")
    print(f"🔑 Session ID: {session_id}")
    
    return session_id

if __name__ == "__main__":
    test_session_memory()
