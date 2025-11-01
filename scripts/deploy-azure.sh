#!/bin/bash

# PrepSmart MVP - Azure Container Apps Deployment Script
# This script deploys both backend and frontend to Azure Container Apps

set -e  # Exit on error

echo "========================================"
echo "PrepSmart MVP - Azure Deployment"
echo "========================================"
echo ""

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-prepsmart-rg}"
LOCATION="${LOCATION:-eastus}"
CONTAINER_APP_ENV="${CONTAINER_APP_ENV:-prepsmart-env}"
ACR_NAME="${ACR_NAME:-prepsmartacr}"
BACKEND_APP_NAME="${BACKEND_APP_NAME:-prepsmart-backend}"
FRONTEND_APP_NAME="${FRONTEND_APP_NAME:-prepsmart-frontend}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Running 'az login'..."
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Using subscription: $SUBSCRIPTION_ID"
echo ""

# Check if Claude API key is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "⚠️  CLAUDE_API_KEY environment variable is not set."
    echo "   Please export it before deploying:"
    echo "   export CLAUDE_API_KEY='your-api-key-here'"
    read -p "Do you want to enter it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter Claude API Key: " CLAUDE_API_KEY
        export CLAUDE_API_KEY
    else
        echo "❌ Deployment cancelled. Please set CLAUDE_API_KEY and try again."
        exit 1
    fi
fi

echo "📦 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Container App Environment: $CONTAINER_APP_ENV"
echo "   Azure Container Registry: $ACR_NAME"
echo "   Backend App: $BACKEND_APP_NAME"
echo "   Frontend App: $FRONTEND_APP_NAME"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# Step 1: Create Resource Group
echo ""
echo "📁 Step 1/8: Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo "✅ Resource group created"

# Step 2: Create Azure Container Registry
echo ""
echo "🐳 Step 2/8: Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none
echo "✅ Container registry created"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo "   ACR Login Server: $ACR_LOGIN_SERVER"

# Step 3: Build and push backend image
echo ""
echo "🔨 Step 3/8: Building and pushing backend image..."
cd backend
az acr build \
    --registry $ACR_NAME \
    --image prepsmart-backend:latest \
    --file Dockerfile \
    . \
    --output table

cd ..
echo "✅ Backend image built and pushed"

# Step 4: Build and push frontend image
echo ""
echo "🔨 Step 4/8: Building and pushing frontend image..."
cd frontend
az acr build \
    --registry $ACR_NAME \
    --image prepsmart-frontend:latest \
    --file Dockerfile \
    . \
    --output table

cd ..
echo "✅ Frontend image built and pushed"

# Step 5: Create Container Apps Environment
echo ""
echo "🌍 Step 5/8: Creating Container Apps environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo "✅ Container Apps environment created"

# Step 6: Deploy Backend Container App
echo ""
echo "🚀 Step 6/8: Deploying backend container app..."
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
        DATABASE_URL=sqlite:///prepsmart.db \
    --output table

BACKEND_URL=$(az containerapp show \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo "✅ Backend deployed at: https://$BACKEND_URL"

# Step 7: Deploy Frontend Container App
echo ""
echo "🚀 Step 7/8: Deploying frontend container app..."
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
    --memory 1Gi \
    --output table

FRONTEND_URL=$(az containerapp show \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo "✅ Frontend deployed at: https://$FRONTEND_URL"

# Step 8: Verify deployment
echo ""
echo "✅ Step 8/8: Verifying deployment..."
sleep 10

echo "   Testing backend health endpoint..."
if curl -s -o /dev/null -w "%{http_code}" https://$BACKEND_URL/api/health | grep -q "200"; then
    echo "   ✅ Backend is healthy"
else
    echo "   ⚠️  Backend health check failed (may still be starting)"
fi

echo ""
echo "========================================"
echo "🎉 Deployment Complete!"
echo "========================================"
echo ""
echo "📍 Your application URLs:"
echo "   Backend:  https://$BACKEND_URL"
echo "   Frontend: https://$FRONTEND_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Update frontend API base URL to: https://$BACKEND_URL"
echo "   2. Test the application at: https://$FRONTEND_URL"
echo "   3. Monitor logs: az containerapp logs show -n $BACKEND_APP_NAME -g $RESOURCE_GROUP"
echo ""
echo "💰 Estimated cost: ~$30-50/month"
echo "   (Container Apps: ~$25/mo, ACR: ~$5/mo, Egress: variable)"
echo ""
