#!/usr/bin/env python3
"""
Targeted Gemini Permissions Diagnostic for Project Pravaah

This script checks the exact permissions and provides specific guidance.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_service_account_permissions():
    """Check what permissions the service account actually has."""
    logger.info("🔍 Checking service account permissions...")
    
    try:
        from google.auth import default
        from google.auth.transport.requests import Request
        import requests
        
        # Set up authentication
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_path)
        
        # Get credentials
        credentials, project = default()
        credentials.refresh(Request())
        
        # Read service account email from key file
        with open(key_path, 'r') as f:
            key_data = json.load(f)
        
        sa_email = key_data.get('client_email')
        
        logger.info(f"📧 Service Account: {sa_email}")
        logger.info(f"🏗️ Project: {project}")
        
        # Check IAM policy for this service account
        iam_url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project}:getIamPolicy"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        
        response = requests.post(iam_url, headers=headers)
        
        if response.status_code == 200:
            iam_policy = response.json()
            bindings = iam_policy.get('bindings', [])
            
            sa_roles = []
            for binding in bindings:
                if sa_email in binding.get('members', []):
                    sa_roles.append(binding.get('role'))
            
            logger.info(f"🎭 Current roles for {sa_email}:")
            for role in sa_roles:
                logger.info(f"   ✅ {role}")
            
            # Check for required roles
            required_roles = [
                'roles/aiplatform.user',
                'roles/ml.admin',
                'roles/ml.developer'
            ]
            
            missing_roles = []
            for role in required_roles:
                if role not in sa_roles:
                    missing_roles.append(role)
            
            if missing_roles:
                logger.error("❌ Missing required roles:")
                for role in missing_roles:
                    logger.error(f"   ❌ {role}")
            else:
                logger.info("✅ All required roles present")
            
            return sa_roles, missing_roles
            
        else:
            logger.error(f"❌ Could not get IAM policy: {response.status_code}")
            return [], []
            
    except Exception as e:
        logger.error(f"❌ Error checking permissions: {e}")
        return [], []

def check_api_status():
    """Check if required APIs are enabled."""
    logger.info("🔌 Checking API status...")
    
    try:
        from google.auth import default
        from google.auth.transport.requests import Request
        import requests
        
        credentials, project = default()
        credentials.refresh(Request())
        
        apis_to_check = [
            'aiplatform.googleapis.com',
            'ml.googleapis.com'
        ]
        
        for api in apis_to_check:
            api_url = f"https://serviceusage.googleapis.com/v1/projects/{project}/services/{api}"
            headers = {"Authorization": f"Bearer {credentials.token}"}
            
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                service_info = response.json()
                state = service_info.get('state', 'UNKNOWN')
                logger.info(f"   {api}: {state}")
            else:
                logger.warning(f"   {api}: Could not check (status: {response.status_code})")
                
    except Exception as e:
        logger.error(f"❌ Error checking APIs: {e}")

def provide_exact_fix():
    """Provide exact steps to fix the issue."""
    logger.info("=" * 60)
    logger.info("🔧 EXACT FIX STEPS")
    logger.info("=" * 60)
    
    logger.info("1. Go to Google Cloud Console:")
    logger.info("   https://console.cloud.google.com/iam-admin/iam?project=stable-sign-454210-i0")
    logger.info("")
    
    logger.info("2. Find your service account:")
    logger.info("   pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com")
    logger.info("")
    
    logger.info("3. Click the pencil (Edit) icon next to it")
    logger.info("")
    
    logger.info("4. Add these EXACT roles (click 'ADD ANOTHER ROLE' for each):")
    logger.info("   - Vertex AI User")
    logger.info("   - AI Platform Admin (if available)")
    logger.info("   - Service Account Token Creator")
    logger.info("")
    
    logger.info("5. If you don't see 'Vertex AI User', try these alternatives:")
    logger.info("   - AI Platform Admin")
    logger.info("   - ML Engine Admin")
    logger.info("   - Editor (broader permissions)")
    logger.info("")
    
    logger.info("6. Save and wait 5-10 minutes")
    logger.info("")
    
    logger.info("7. Re-run: python verify_gemini_permissions.py")

def main():
    """Main diagnostic function."""
    logger.info("🚀 Starting Targeted Gemini Permissions Check")
    logger.info("=" * 60)
    
    # Check current permissions
    current_roles, missing_roles = check_service_account_permissions()
    
    # Check API status
    check_api_status()
    
    # Provide fix
    provide_exact_fix()
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
