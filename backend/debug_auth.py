#!/usr/bin/env python3
"""
Authentication Debug Script for Project Pravaah

This script helps debug Google Cloud authentication issues for local development.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_service_account_key():
    """Check if service account key exists and is valid."""
    logger.info("🔍 Checking service account key...")
    
    # Check if file exists
    key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    
    if not os.path.exists(key_path):
        logger.error(f"❌ Service account key not found at: {key_path}")
        return False
    
    logger.info(f"✅ Service account key found at: {key_path}")
    
    # Check if file is valid JSON
    try:
        with open(key_path, 'r') as f:
            key_data = json.load(f)
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in key_data]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields in service account key: {missing_fields}")
            return False
        
        logger.info(f"✅ Service account key is valid JSON")
        logger.info(f"   Project ID: {key_data.get('project_id')}")
        logger.info(f"   Client Email: {key_data.get('client_email')}")
        
        return True, key_data
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Service account key is not valid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error reading service account key: {e}")
        return False

def check_environment_variables():
    """Check current environment variables."""
    logger.info("🌍 Checking environment variables...")
    
    # Check GOOGLE_APPLICATION_CREDENTIALS
    gac = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if gac:
        logger.info(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set: {gac}")
        if os.path.exists(gac):
            logger.info("✅ GOOGLE_APPLICATION_CREDENTIALS file exists")
        else:
            logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS file does not exist")
    else:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS is not set")
    
    # Check other relevant env vars
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCP_PROJECT')
    if project_id:
        logger.info(f"✅ Google Cloud Project ID found in environment: {project_id}")
    else:
        logger.info("ℹ️ No Google Cloud Project ID found in environment variables")

def test_firebase_admin():
    """Test Firebase Admin SDK initialization."""
    logger.info("🔥 Testing Firebase Admin SDK...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Set up service account path
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        
        # Try to initialize Firebase Admin SDK
        try:
            # Check if already initialized
            firebase_admin.get_app()
            logger.info("✅ Firebase Admin SDK already initialized")
        except ValueError:
            # Initialize with service account
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase Admin SDK initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase Admin SDK initialization failed: {e}")
        return False

def test_vertex_ai():
    """Test Vertex AI initialization."""
    logger.info("🧠 Testing Vertex AI...")
    
    try:
        import vertexai
        
        # Set environment variable for authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
        
        # Initialize Vertex AI
        vertexai.init(project="stable-sign-454210-i0", location="asia-south1")
        logger.info("✅ Vertex AI initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Vertex AI initialization failed: {e}")
        return False

def test_firestore():
    """Test Firestore client initialization."""
    logger.info("🗄️ Testing Firestore...")
    
    try:
        from google.cloud import firestore
        
        # Set environment variable for authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
        
        # Initialize Firestore client
        db = firestore.Client(project="stable-sign-454210-i0")
        logger.info("✅ Firestore client initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firestore initialization failed: {e}")
        return False

def set_environment_credentials():
    """Set GOOGLE_APPLICATION_CREDENTIALS environment variable."""
    logger.info("🔧 Setting up authentication environment...")
    
    key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    abs_key_path = os.path.abspath(key_path)
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = abs_key_path
    logger.info(f"✅ Set GOOGLE_APPLICATION_CREDENTIALS to: {abs_key_path}")
    
    return abs_key_path

def main():
    """Main debugging function."""
    logger.info("🚀 Starting Project Pravaah Authentication Debug")
    logger.info("=" * 60)
    
    # Step 1: Check service account key
    key_result = check_service_account_key()
    if not key_result:
        logger.error("❌ Service account key check failed. Cannot proceed.")
        return 1
    
    # Step 2: Check environment variables
    check_environment_variables()
    
    # Step 3: Set up authentication environment
    set_environment_credentials()
    
    # Step 4: Test individual services
    logger.info("\n🧪 Testing Google Cloud Services...")
    
    firebase_ok = test_firebase_admin()
    firestore_ok = test_firestore()
    vertex_ok = test_vertex_ai()
    
    # Summary
    logger.info("=" * 60)
    if all([firebase_ok, firestore_ok, vertex_ok]):
        logger.info("🎉 ALL AUTHENTICATION TESTS PASSED!")
        logger.info("✅ Your integration test should now work properly.")
        logger.info("🚀 Try running: python test_integration.py")
    else:
        logger.error("❌ Some authentication tests failed.")
        logger.info("💡 Check your service account permissions for:")
        logger.info("   - Firebase Admin SDK")
        logger.info("   - Firestore Database")
        logger.info("   - Vertex AI")
        logger.info("   - Pub/Sub (if needed)")
    
    logger.info("=" * 60)
    return 0 if all([firebase_ok, firestore_ok, vertex_ok]) else 1

if __name__ == "__main__":
    exit(main())
