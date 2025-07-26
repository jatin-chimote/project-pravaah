# Gemini (Vertex AI) Permissions Setup Guide for Project Pravaah

## Current Issue
Your integration test shows: `401 Request had invalid authentication credentials` when calling Gemini API.

## Required Google Cloud Setup

### 1. Enable Vertex AI API
```bash
# Enable the Vertex AI API in your project
gcloud services enable aiplatform.googleapis.com --project=stable-sign-454210-i0
```

### 2. Grant Required IAM Roles to Service Account

Your service account: `pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com`

**Required Roles:**
```bash
# Grant Vertex AI User role (most important for Gemini)
gcloud projects add-iam-policy-binding stable-sign-454210-i0 \
    --member="serviceAccount:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Grant ML Developer role (for model access)
gcloud projects add-iam-policy-binding stable-sign-454210-i0 \
    --member="serviceAccount:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com" \
    --role="roles/ml.developer"

# Grant Service Account Token Creator (if deploying to Cloud Run)
gcloud projects add-iam-policy-binding stable-sign-454210-i0 \
    --member="serviceAccount:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountTokenCreator"
```

### 3. Verify API is Enabled
```bash
# Check if Vertex AI API is enabled
gcloud services list --enabled --project=stable-sign-454210-i0 | grep aiplatform
```

### 4. Test Gemini Access
```bash
# Test if your service account can access Vertex AI
gcloud auth activate-service-account --key-file=serviceAccountKey.json
gcloud ai models list --region=asia-south1 --project=stable-sign-454210-i0
```

## Alternative: Using Google Cloud Console

### Via Google Cloud Console UI:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select Project**: `stable-sign-454210-i0`
3. **Enable Vertex AI API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Vertex AI API"
   - Click "Enable"

4. **Grant IAM Roles**:
   - Go to "IAM & Admin" > "IAM"
   - Find your service account: `pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com`
   - Click "Edit" (pencil icon)
   - Add these roles:
     - `Vertex AI User` (roles/aiplatform.user)
     - `ML Developer` (roles/ml.developer)
     - `Service Account Token Creator` (roles/iam.serviceAccountTokenCreator)

## Verification Steps

### Test 1: Check Service Account Permissions
```bash
# List current IAM bindings for your service account
gcloud projects get-iam-policy stable-sign-454210-i0 \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com"
```

### Test 2: Test Vertex AI Access
Run our debug script to test Vertex AI access:
```bash
python debug_auth.py
```

### Test 3: Run Integration Test
After setting permissions, run the integration test:
```bash
python test_integration.py
```

## Expected Results After Fix

When permissions are correctly set, you should see:
- ✅ No more "401 authentication" errors
- ✅ Gemini API calls succeed
- ✅ Real AI-driven strategic decisions instead of fallback logic
- ✅ Integration test shows actual Gemini recommendations

## Troubleshooting

### If you still get 401 errors:
1. **Wait 5-10 minutes** after setting permissions (IAM changes can take time)
2. **Regenerate service account key** if it's old
3. **Check quotas** in Vertex AI console
4. **Verify region** - ensure you're using `asia-south1`

### If you get quota errors:
- Vertex AI has usage limits for new projects
- Request quota increase in Google Cloud Console
- Consider using a different region if needed

## Security Note
- Never commit `serviceAccountKey.json` to version control
- Use environment variables for production deployments
- Consider using Workload Identity for GKE/Cloud Run deployments
