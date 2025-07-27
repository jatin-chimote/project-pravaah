#!/usr/bin/env python3
"""
Project Pravaah - Database Verification Script
==============================================
Verifies database connection and lists available databases
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as firestore_client
import os

def verify_database_connection():
    """Verify connection to Project Pravaah database"""
    
    print("🔍 Project Pravaah Database Verification")
    print("=" * 50)
    
    # Check current gcloud project
    try:
        import subprocess
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        current_project = result.stdout.strip()
        print(f"📋 Current gcloud project: {current_project}")
    except:
        print("⚠️ Could not determine current gcloud project")
    
    print(f"🎯 Target project: stable-sign-454210-i0")
    print(f"🗄️ Target database: project-pravaah")
    print()
    
    # Initialize Firebase Admin
    try:
        cred = credentials.ApplicationDefault()
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': 'stable-sign-454210-i0',
            })
        print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"❌ Firebase Admin SDK initialization failed: {e}")
        return
    
    # Test different database connection methods
    print("\n🧪 Testing database connections...")
    print("-" * 30)
    
    # Method 1: Try connecting to named database 'project-pravaah'
    try:
        print("1️⃣ Attempting to connect to database 'project-pravaah'...")
        db1 = firestore.client(database='project-pravaah')
        
        # Test a simple operation
        test_doc = db1.collection('_test').document('connection_test')
        test_doc.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
        
        print("✅ SUCCESS: Connected to database 'project-pravaah'")
        
        # Clean up test document
        test_doc.delete()
        
    except Exception as e:
        print(f"❌ FAILED: Could not connect to database 'project-pravaah': {e}")
    
    # Method 2: Try connecting to default database
    try:
        print("\n2️⃣ Attempting to connect to default database...")
        db2 = firestore.client()
        
        # Test a simple operation
        test_doc = db2.collection('_test').document('connection_test')
        test_doc.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
        
        print("✅ SUCCESS: Connected to default database")
        
        # Clean up test document
        test_doc.delete()
        
    except Exception as e:
        print(f"❌ FAILED: Could not connect to default database: {e}")
    
    # Method 3: Try using google-cloud-firestore directly
    try:
        print("\n3️⃣ Attempting direct connection with google-cloud-firestore...")
        direct_client = firestore_client.Client(
            project='stable-sign-454210-i0',
            database='project-pravaah'
        )
        
        # Test a simple operation
        test_doc = direct_client.collection('_test').document('connection_test')
        test_doc.set({'test': True, 'timestamp': firestore_client.SERVER_TIMESTAMP})
        
        print("✅ SUCCESS: Direct connection to 'project-pravaah' database")
        
        # Clean up test document
        test_doc.delete()
        
    except Exception as e:
        print(f"❌ FAILED: Direct connection failed: {e}")
    
    # Method 4: List available databases
    try:
        print("\n4️⃣ Listing available databases...")
        from google.cloud import firestore_admin_v1
        
        admin_client = firestore_admin_v1.FirestoreAdminClient()
        parent = f"projects/stable-sign-454210-i0"
        
        databases = admin_client.list_databases(parent=parent)
        print("📋 Available databases:")
        for db in databases:
            db_name = db.name.split('/')[-1]
            print(f"   - {db_name}")
            
    except Exception as e:
        print(f"⚠️ Could not list databases: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Recommendations:")
    print("1. If method 1 works: Use database='project-pravaah'")
    print("2. If method 2 works: Use default database (no database parameter)")
    print("3. If method 3 works: Use google-cloud-firestore directly")
    print("4. Check the database list above for exact database names")
    print("=" * 50)

if __name__ == "__main__":
    verify_database_connection()
