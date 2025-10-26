#!/usr/bin/env python3
"""
Simple Firebase connection test script
"""
import os
import sys
import time

# Set environment variable
os.environ['FIREBASE_CREDENTIALS_PATH'] = './lambda-59fe8-firebase-adminsdk-fbsvc-977075cada.json'

try:
    print("Importing Firebase modules...")
    from app.firebase_db import FirebaseDatabase
    print("✓ Firebase modules imported successfully")
    
    print("Creating FirebaseDatabase instance...")
    db = FirebaseDatabase()
    print("✓ FirebaseDatabase created successfully")
    
    print("Testing list_projects() with timeout...")
    start_time = time.time()
    
    # Set a timeout for the operation
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out after 10 seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    try:
        projects = db.list_projects()
        signal.alarm(0)  # Cancel the alarm
        
        elapsed = time.time() - start_time
        print(f"✓ list_projects() completed in {elapsed:.2f} seconds")
        print(f"✓ Found {len(projects)} projects")
        
        if projects:
            print("Sample project:")
            print(f"  - ID: {projects[0].get('project_id', 'N/A')}")
            print(f"  - Name: {projects[0].get('project_name', 'N/A')}")
        else:
            print("No projects found in database")
            
    except TimeoutError:
        signal.alarm(0)
        elapsed = time.time() - start_time
        print(f"✗ list_projects() timed out after {elapsed:.2f} seconds")
    except Exception as e:
        signal.alarm(0)
        elapsed = time.time() - start_time
        print(f"✗ list_projects() failed after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"✗ Failed to initialize Firebase: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Test completed successfully!")
