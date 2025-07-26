#!/usr/bin/env python3
"""
Gemini Permissions Verification Script for Project Pravaah

This script helps verify that your service account has the correct permissions
to use Vertex AI (Gemini) API.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_service_account_details():
    """Check service account details from the key file."""
    logger.info("🔍 Checking service account details...")
    
    key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    
    try:
        with open(key_path, 'r') as f:
            key_data = json.load(f)
        
        project_id = key_data.get('project_id')
        client_email = key_data.get('client_email')
        
        logger.info(f"✅ Project ID: {project_id}")
        logger.info(f"✅ Service Account: {client_email}")
        
        # Check if it matches expected values
        expected_project = "stable-sign-454210-i0"
        expected_sa = "pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com"
        
        if project_id == expected_project:
            logger.info("✅ Project ID matches expected value")
        else:
            logger.warning(f"⚠️ Project ID mismatch. Expected: {expected_project}, Got: {project_id}")
        
        if client_email == expected_sa:
            logger.info("✅ Service account matches expected value")
        else:
            logger.warning(f"⚠️ Service account mismatch. Expected: {expected_sa}, Got: {client_email}")
        
        return True, key_data
        
    except Exception as e:
        logger.error(f"❌ Error reading service account key: {e}")
        return False, None

def test_vertex_ai_basic():
    """Test basic Vertex AI initialization."""
    logger.info("🧠 Testing Vertex AI basic initialization...")
    
    try:
        import vertexai
        
        # Set up authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_path)
        
        # Initialize Vertex AI
        vertexai.init(project="stable-sign-454210-i0", location="asia-south1")
        logger.info("✅ Vertex AI initialization successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Vertex AI initialization failed: {e}")
        return False

def test_gemini_model_access():
    """Test if we can access the Gemini model."""
    logger.info("🤖 Testing Gemini model access...")
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Set up authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_path)
        
        # Initialize Vertex AI
        vertexai.init(project="stable-sign-454210-i0", location="asia-south1")
        
        # Try to create Gemini model instance
        model = GenerativeModel("gemini-1.5-pro")
        logger.info("✅ Gemini model instance created successfully")
        
        return True, model
        
    except Exception as e:
        logger.error(f"❌ Gemini model access failed: {e}")
        return False, None

def test_gemini_api_call():
    """Test an actual Gemini API call."""
    logger.info("🚀 Testing actual Gemini API call...")
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Set up authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_path)
        
        # Initialize Vertex AI
        vertexai.init(project="stable-sign-454210-i0", location="asia-south1")
        
        # Create model and make a simple test call
        model = GenerativeModel("gemini-1.5-pro")
        
        test_prompt = """
You are testing the Gemini API for Project Pravaah traffic management system.
Respond with exactly this JSON format:
{
  "status": "success",
  "message": "Gemini API is working correctly",
  "test_passed": true
}
"""
        
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            logger.info("✅ Gemini API call successful!")
            logger.info(f"📝 Response: {response.text[:200]}...")
            return True, response.text
        else:
            logger.error("❌ Gemini API returned empty response")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Gemini API call failed: {e}")
        
        # Provide specific guidance based on error type
        error_str = str(e)
        if "401" in error_str or "authentication" in error_str.lower():
            logger.error("🔧 AUTHENTICATION ERROR - Your service account needs proper permissions!")
            logger.error("   Run the commands in setup_gemini_permissions.md to fix this.")
        elif "403" in error_str or "permission" in error_str.lower():
            logger.error("🔧 PERMISSION ERROR - Missing required IAM roles!")
            logger.error("   Your service account needs 'Vertex AI User' role.")
        elif "quota" in error_str.lower():
            logger.error("🔧 QUOTA ERROR - API usage limits exceeded!")
            logger.error("   Check your Vertex AI quotas in Google Cloud Console.")
        
        return False, str(e)

def provide_setup_guidance():
    """Provide setup guidance based on test results."""
    logger.info("=" * 60)
    logger.info("🔧 SETUP GUIDANCE")
    logger.info("=" * 60)
    
    logger.info("To fix Gemini authentication issues, run these commands:")
    logger.info("")
    logger.info("1. Enable Vertex AI API:")
    logger.info("   gcloud services enable aiplatform.googleapis.com --project=stable-sign-454210-i0")
    logger.info("")
    logger.info("2. Grant required IAM roles:")
    logger.info("   gcloud projects add-iam-policy-binding stable-sign-454210-i0 \\")
    logger.info("       --member=\"serviceAccount:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com\" \\")
    logger.info("       --role=\"roles/aiplatform.user\"")
    logger.info("")
    logger.info("   gcloud projects add-iam-policy-binding stable-sign-454210-i0 \\")
    logger.info("       --member=\"serviceAccount:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com\" \\")
    logger.info("       --role=\"roles/ml.developer\"")
    logger.info("")
    logger.info("3. Wait 5-10 minutes for IAM changes to propagate")
    logger.info("")
    logger.info("4. Re-run this verification script: python verify_gemini_permissions.py")
    logger.info("")
    logger.info("📖 For detailed instructions, see: setup_gemini_permissions.md")

def main():
    """Main verification function."""
    logger.info("🚀 Starting Gemini Permissions Verification")
    logger.info("=" * 60)
    
    # Step 1: Check service account details
    sa_ok, sa_data = check_service_account_details()
    if not sa_ok:
        logger.error("❌ Cannot proceed without valid service account key")
        return 1
    
    # Step 2: Test Vertex AI basic initialization
    vertexai_ok = test_vertex_ai_basic()
    
    # Step 3: Test Gemini model access
    model_ok, model = test_gemini_model_access()
    
    # Step 4: Test actual API call
    api_ok, api_response = test_gemini_api_call()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Service Account Key: {'✅ Valid' if sa_ok else '❌ Invalid'}")
    logger.info(f"Vertex AI Init: {'✅ Success' if vertexai_ok else '❌ Failed'}")
    logger.info(f"Gemini Model Access: {'✅ Success' if model_ok else '❌ Failed'}")
    logger.info(f"Gemini API Call: {'✅ Success' if api_ok else '❌ Failed'}")
    
    if all([sa_ok, vertexai_ok, model_ok, api_ok]):
        logger.info("=" * 60)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("✅ Your Gemini integration is ready to use!")
        logger.info("🚀 Run the integration test: python test_integration.py")
        logger.info("=" * 60)
        return 0
    else:
        logger.info("=" * 60)
        logger.error("❌ SOME TESTS FAILED")
        logger.error("🔧 Follow the setup guidance below to fix issues")
        provide_setup_guidance()
        logger.info("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
