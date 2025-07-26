# Project Pravaah - Deployment Checklist

## Pre-Deployment Requirements

### ✅ Google Cloud Setup
- [ ] Access to Google Cloud Console
- [ ] Project ID: `stable-sign-454210-i0` exists and accessible
- [ ] Billing account enabled for the project
- [ ] Owner or Editor permissions on the project

### ✅ Service Account Setup
- [ ] Service account: `pravaah-agent-runner@stable-sign-454210-i0.iam.gserviceaccount.com` exists
- [ ] Service account has required IAM roles:
  - [ ] Cloud Run Admin
  - [ ] Cloud Build Service Account
  - [ ] Artifact Registry Administrator
  - [ ] Service Account User
  - [ ] Vertex AI User (for Gemini)
  - [ ] Firebase Admin SDK Admin Service Agent

### ✅ Files Ready for Upload
- [ ] `deploy.sh` script
- [ ] `api_gateway_service/` directory with:
  - [ ] `main.py`
  - [ ] `Dockerfile`
  - [ ] `requirements.txt`
- [ ] `agents/` directory with ADK agent files:
  - [ ] `adk_observer_agent.py`
  - [ ] `adk_simulation_agent.py`
  - [ ] `adk_orchestrator_agent.py`
  - [ ] `adk_communications_agent.py`
  - [ ] Individual Dockerfiles for each agent service

## Deployment Steps

### 1. Google Cloud Shell Access
```bash
# Open Cloud Shell at console.cloud.google.com
# Verify project
gcloud config get-value project
```

### 2. Upload Files
```bash
# Upload backend folder via Cloud Shell Editor
# Or clone from Git repository
```

### 3. Set Permissions
```bash
chmod +x deploy.sh
```

### 4. Run Deployment
```bash
./deploy.sh
```

### 5. Verify Deployment
```bash
# Check deployed services
gcloud run services list --region=asia-south1

# Test API Gateway
curl https://api-gateway-service-[HASH]-uc.a.run.app/health
```

## Expected Deployment Time
- **Total Time**: 15-25 minutes
- **API Enablement**: 2-3 minutes
- **Artifact Registry Setup**: 1-2 minutes
- **Container Builds**: 10-15 minutes (5 services × 2-3 min each)
- **Cloud Run Deployments**: 3-5 minutes
- **IAM Configuration**: 1-2 minutes

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure you have Owner/Editor role on the project
2. **API Not Enabled**: Script will enable APIs automatically
3. **Build Failures**: Check Dockerfile syntax and dependencies
4. **Service Account Issues**: Verify service account exists and has correct roles

### Useful Commands
```bash
# Check build logs
gcloud builds list --limit=10

# Check service logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Describe service
gcloud run services describe api-gateway-service --region=asia-south1
```

## Post-Deployment Verification

### ✅ Services Health Check
- [ ] API Gateway: `GET /health` returns 200
- [ ] All services show "READY" status in Cloud Run console
- [ ] No error logs in Cloud Logging

### ✅ Security Verification
- [ ] API Gateway is publicly accessible
- [ ] Internal services (orchestrator, agents) are private
- [ ] Service-to-service authentication configured

### ✅ Functional Testing
- [ ] API Gateway `/docs` endpoint accessible
- [ ] Test `/run_orchestration` endpoint with sample data
- [ ] Verify A2A communication between services

## Success Indicators
✅ All 5 services deployed successfully
✅ Public API Gateway URL available
✅ Health checks passing
✅ No critical errors in logs
✅ Ready for Angular frontend integration

---

**Next Steps After Deployment:**
1. Configure Angular frontend with API Gateway URL
2. Set up monitoring and alerting
3. Configure custom domain (optional)
4. Set up CI/CD pipeline for future deployments
