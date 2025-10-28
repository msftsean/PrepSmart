# PrepSmart MVP - Azure Container Apps Deployment Guide

This guide will walk you through deploying PrepSmart to Azure Container Apps.

## Prerequisites

1. **Azure Account**
   - Active Azure subscription
   - Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

2. **Claude API Key**
   - Anthropic API key with access to Claude Sonnet 4.5
   - Get it from: https://console.anthropic.com/

3. **Docker** (Optional - for local testing)
   - Docker Desktop or Docker Engine
   - Only needed if you want to test containers locally first

## Quick Deployment (Automated)

The easiest way to deploy is using our automated script:

```bash
# 1. Set your Claude API key
export CLAUDE_API_KEY='sk-ant-api03-your-key-here'

# 2. Login to Azure
az login

# 3. Run deployment script
./deploy-azure.sh
```

That's it! The script will:
- Create all Azure resources
- Build and push Docker images
- Deploy backend and frontend
- Configure networking and scaling

## Manual Deployment (Step by Step)

If you prefer to deploy manually or customize the deployment:

### Step 1: Set Environment Variables

```bash
export RESOURCE_GROUP="prepsmart-rg"
export LOCATION="eastus"
export CONTAINER_APP_ENV="prepsmart-env"
export ACR_NAME="prepsmartacr"  # Must be globally unique
export BACKEND_APP_NAME="prepsmart-backend"
export FRONTEND_APP_NAME="prepsmart-frontend"
export CLAUDE_API_KEY="your-claude-api-key"
```

### Step 2: Create Resource Group

```bash
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION
```

### Step 3: Create Azure Container Registry

```bash
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
```

### Step 4: Build and Push Images

```bash
# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Build and push backend
cd backend
az acr build \
    --registry $ACR_NAME \
    --image prepsmart-backend:latest \
    --file Dockerfile \
    .

# Build and push frontend
cd ../frontend
az acr build \
    --registry $ACR_NAME \
    --image prepsmart-frontend:latest \
    --file Dockerfile \
    .
cd ..
```

### Step 5: Create Container Apps Environment

```bash
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

### Step 6: Deploy Backend

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

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

### Step 7: Deploy Frontend

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

### Step 8: Get Application URLs

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo "Backend:  https://$BACKEND_URL"
echo "Frontend: https://$FRONTEND_URL"
```

## Post-Deployment Configuration

### Update Frontend API Configuration

The frontend needs to know the backend URL. Update [frontend/assets/js/api-client.js](frontend/assets/js/api-client.js):

```javascript
const API_BASE_URL = 'https://your-backend-url.azurecontainerapps.io';
```

Then rebuild and redeploy the frontend:

```bash
cd frontend
az acr build --registry $ACR_NAME --image prepsmart-frontend:latest .
az containerapp update --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP
```

## Monitoring and Management

### View Logs

```bash
# Backend logs
az containerapp logs show \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --follow

# Frontend logs
az containerapp logs show \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --follow
```

### Check Health

```bash
# Backend health
curl https://$BACKEND_URL/api/health

# Frontend health
curl https://$FRONTEND_URL/
```

### Scale Applications

```bash
# Scale backend
az containerapp update \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 2 \
    --max-replicas 5

# Scale frontend
az containerapp update \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 1 \
    --max-replicas 3
```

### Update Environment Variables

```bash
# Update Claude API key
az containerapp update \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars CLAUDE_API_KEY="new-key-here"
```

## Cost Optimization

### Development Environment
For testing/development, use minimal resources:

```bash
# Backend: 0.5 CPU, 1Gi memory, 1 replica
# Frontend: 0.25 CPU, 0.5Gi memory, 1 replica
# Estimated cost: ~$15-20/month
```

### Production Environment
For production with auto-scaling:

```bash
# Backend: 1.0 CPU, 2Gi memory, 1-3 replicas
# Frontend: 0.5 CPU, 1Gi memory, 1-2 replicas
# Estimated cost: ~$30-50/month + API costs
```

### Cost Breakdown
- **Container Apps**: ~$25-40/month (consumption-based)
- **Azure Container Registry**: ~$5/month (Basic tier)
- **Egress (data transfer)**: Variable, ~$0-10/month
- **Claude API**: Variable, based on usage (~$0.06 per request)

## Troubleshooting

### Backend fails to start

Check logs:
```bash
az containerapp logs show -n $BACKEND_APP_NAME -g $RESOURCE_GROUP --tail 50
```

Common issues:
- Missing Claude API key
- Image build failed
- Port configuration incorrect (should be 5000)

### Frontend can't connect to backend

1. Verify backend is running:
   ```bash
   curl https://$BACKEND_URL/api/health
   ```

2. Check CORS configuration in backend
3. Update frontend API_BASE_URL
4. Check network connectivity

### Database issues

SQLite is used by default and stores data in the container. For persistent storage, consider:
- Azure Database for PostgreSQL
- Azure Cosmos DB
- Mounted volumes (Azure Files)

### API rate limits

Monitor Claude API usage and implement:
- Request caching
- Rate limiting on frontend
- Queue system for high-load scenarios

## Security Best Practices

1. **Use Azure Key Vault for secrets**
   ```bash
   # Store Claude API key in Key Vault
   az keyvault create --name prepsmart-kv -g $RESOURCE_GROUP
   az keyvault secret set --vault-name prepsmart-kv --name claude-api-key --value "$CLAUDE_API_KEY"
   ```

2. **Enable managed identity**
   ```bash
   az containerapp identity assign -n $BACKEND_APP_NAME -g $RESOURCE_GROUP
   ```

3. **Restrict ingress**
   ```bash
   # Make backend internal-only if accessed through frontend
   az containerapp ingress update \
       -n $BACKEND_APP_NAME \
       -g $RESOURCE_GROUP \
       --type internal
   ```

4. **Enable HTTPS only** (already enabled by default)

5. **Regular updates**
   ```bash
   # Rebuild with latest security patches
   az acr build --registry $ACR_NAME --image prepsmart-backend:latest ./backend
   az containerapp update -n $BACKEND_APP_NAME -g $RESOURCE_GROUP
   ```

## Cleanup

To remove all resources and stop incurring costs:

```bash
# Delete entire resource group
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Or delete individual resources
az containerapp delete -n $BACKEND_APP_NAME -g $RESOURCE_GROUP --yes
az containerapp delete -n $FRONTEND_APP_NAME -g $RESOURCE_GROUP --yes
az containerapp env delete -n $CONTAINER_APP_ENV -g $RESOURCE_GROUP --yes
az acr delete -n $ACR_NAME -g $RESOURCE_GROUP --yes
```

## Support

For issues:
- Azure Container Apps docs: https://docs.microsoft.com/en-us/azure/container-apps/
- Anthropic Claude docs: https://docs.anthropic.com/
- GitHub Issues: [Your repository URL]

## Next Steps

- [ ] Set up CI/CD with GitHub Actions
- [ ] Configure custom domain
- [ ] Enable Application Insights monitoring
- [ ] Set up automated backups
- [ ] Implement Redis cache for API responses
- [ ] Add Azure Front Door for CDN/WAF
