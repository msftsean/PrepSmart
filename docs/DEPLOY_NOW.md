# 🚀 Deploy PrepSmart to Azure - Quick Start

## Option 1: Deploy from Azure Cloud Shell (Recommended)

Azure Cloud Shell is the easiest way to deploy as it's already authenticated.

### Steps:

1. **Open Azure Cloud Shell** at https://shell.azure.com

2. **Clone your repository** (or upload the files):
   ```bash
   git clone <your-repo-url>
   cd prepsmart
   ```

3. **Set your Claude API key**:
   ```bash
   export CLAUDE_API_KEY='your-claude-api-key-here'
   ```

   > Get your API key from https://console.anthropic.com/

4. **Run the deployment script**:
   ```bash
   chmod +x deploy-azure.sh
   ./deploy-azure.sh
   ```

5. **Wait 5-10 minutes** for deployment to complete

6. **Get your URLs** from the script output:
   ```
   Backend:  https://prepsmart-backend-XXXXX.azurecontainerapps.io
   Frontend: https://prepsmart-frontend-XXXXX.azurecontainerapps.io
   ```

---

## Option 2: Manual Deployment Steps

If you prefer step-by-step control:

### 1. Login to Azure
```bash
az login
```

### 2. Set Variables
```bash
export RESOURCE_GROUP="prepsmart-rg"
export LOCATION="eastus"
export CONTAINER_APP_ENV="prepsmart-env"
export ACR_NAME="prepsmartacr$(date +%s)"  # Unique name
export BACKEND_APP_NAME="prepsmart-backend"
export FRONTEND_APP_NAME="prepsmart-frontend"
export CLAUDE_API_KEY='your-claude-api-key-here'
```

### 3. Create Resources
```bash
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create container registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR info
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
```

### 4. Build and Push Images
```bash
# Backend
cd backend
az acr build --registry $ACR_NAME --image prepsmart-backend:latest .

# Frontend
cd ../frontend
az acr build --registry $ACR_NAME --image prepsmart-frontend:latest .
cd ..
```

### 5. Create Container Apps Environment
```bash
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

### 6. Deploy Backend
```bash
az containerapp create \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_LOGIN_SERVER/prepsmart-backend:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 5000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 1.0 \
    --memory 2Gi \
    --env-vars \
        CLAUDE_API_KEY="$CLAUDE_API_KEY" \
        FLASK_ENV=production \
        DATABASE_URL=sqlite:///prepsmart.db
```

### 7. Deploy Frontend
```bash
az containerapp create \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_LOGIN_SERVER/prepsmart-frontend:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 80 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 0.5 \
    --memory 1Gi
```

### 8. Get URLs
```bash
BACKEND_URL=$(az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
FRONTEND_URL=$(az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo "Backend:  https://$BACKEND_URL"
echo "Frontend: https://$FRONTEND_URL"
```

---

## Option 3: Deploy Using Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Create Container Apps** manually through the UI
3. **Upload Docker images** to Azure Container Registry
4. **Configure environment variables** in the portal

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed portal instructions.

---

## Post-Deployment: Update Frontend Config

After deployment, update the frontend to use your backend URL:

1. **Edit** `frontend/assets/js/api-client.js`:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.azurecontainerapps.io';
   ```

2. **Rebuild and redeploy frontend**:
   ```bash
   cd frontend
   az acr build --registry $ACR_NAME --image prepsmart-frontend:latest .
   az containerapp update --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP
   ```

---

## Verify Deployment

```bash
# Test backend
curl https://$BACKEND_URL/api/health

# Should return:
# {"dependencies":{"claude_api":"up","database":"up"},"status":"healthy","timestamp":"..."}

# Test frontend
curl https://$FRONTEND_URL/

# Should return HTML
```

---

## Troubleshooting

### Backend fails to start
```bash
az containerapp logs show -n prepsmart-backend -g prepsmart-rg --tail 50
```

### Frontend can't connect to backend
1. Verify backend is running: `curl https://$BACKEND_URL/api/health`
2. Update frontend API URL
3. Check CORS settings

### Cost concerns
```bash
# Scale down to minimum for testing
az containerapp update -n prepsmart-backend -g prepsmart-rg --min-replicas 0 --max-replicas 1
az containerapp update -n prepsmart-frontend -g prepsmart-rg --min-replicas 0 --max-replicas 1
```

---

## Delete Resources (Cleanup)

When you're done testing:

```bash
az group delete --name prepsmart-rg --yes --no-wait
```

This removes all resources and stops billing.

---

## Estimated Timeline

- Azure login: 1 minute
- Resource creation: 2-3 minutes
- Image builds: 3-5 minutes (backend + frontend)
- Container deployment: 2-3 minutes
- **Total: 8-12 minutes**

---

## Cost Estimate

**Monthly costs:**
- Container Apps: $25-40/month
- Container Registry: $5/month
- **Total: ~$30-50/month**

For testing only (minimal usage): ~$5-15/month

---

## Need Help?

- Full documentation: [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
- Azure Container Apps docs: https://docs.microsoft.com/en-us/azure/container-apps/
- Issues: Open a GitHub issue

---

**Ready to deploy?** Open [Azure Cloud Shell](https://shell.azure.com) and run `./deploy-azure.sh`
