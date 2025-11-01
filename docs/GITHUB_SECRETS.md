# GitHub Secrets Configuration

This document explains how to configure GitHub Secrets for secure CI/CD deployment of PrepSmart.

## 🔐 Required Secrets

### For GitHub Actions Deployment

If you plan to deploy PrepSmart automatically via GitHub Actions, you'll need to configure these secrets in your repository settings.

### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret below

---

## Required Secrets List

### 1. `CLAUDE_API_KEY`

**Description**: Your Anthropic Claude API key for AI agent functionality

**How to get it**:
- Go to https://console.anthropic.com/
- Sign up or log in
- Navigate to **API Keys**
- Click **Create Key**
- Copy the key (starts with `sk-ant-api03-`)

**Value format**: `sk-ant-api03-xxxxxxxxxxxxx...`

---

### 2. `AZURE_CREDENTIALS` (Optional - for Azure deployment)

**Description**: Service principal credentials for Azure deployment

**How to get it**:

```bash
az ad sp create-for-rbac \
  --name "prepsmart-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

**Value format**: JSON object containing:
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "xxx",
  "tenantId": "xxx"
}
```

---

### 3. `FLASK_SECRET_KEY`

**Description**: Secret key for Flask session management

**How to generate**:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Value format**: 64-character hex string

---

### 4. `ACR_NAME` (Optional - for Azure Container Registry)

**Description**: Your Azure Container Registry name

**Value format**: `prepsmartacr` (lowercase, no special characters)

---

### 5. `RESOURCE_GROUP` (Optional - for Azure)

**Description**: Azure resource group name

**Value format**: `prepsmart-rg`

---

## 🛡️ Security Best Practices

### DO ✅

- **Rotate secrets regularly** - Change API keys every 90 days
- **Use different keys for dev/staging/prod** - Never reuse production keys
- **Limit secret scope** - Only give access to required workflows
- **Enable secret scanning** - Let GitHub detect leaked secrets
- **Use environment-specific secrets** - Separate dev and prod configs
- **Document who has access** - Keep track of team members with secret access

### DON'T ❌

- **Never commit secrets to git** - Not even in private repos
- **Don't share secrets in Slack/email** - Use secure password managers
- **Don't print secrets in logs** - Mask them in CI/CD output
- **Don't use weak secret keys** - Always generate cryptographically secure keys
- **Don't store secrets in code comments** - Remove before committing
- **Don't expose secrets in error messages** - Handle errors gracefully

---

## 🔍 Secret Scanning

PrepSmart includes automatic secret scanning via:

1. **GitHub Secret Scanning** (automatic for public repos)
2. **Gitleaks** (via GitHub Actions)
3. **detect-secrets** (via pre-commit hooks)

### If a Secret is Leaked

1. **Immediately rotate the secret**
   ```bash
   # For Claude API key: Generate new one at console.anthropic.com
   # For Azure: Regenerate service principal
   ```

2. **Update GitHub Secrets**
   - Replace old secret with new one in repository settings

3. **Update production environment**
   ```bash
   # Azure Container Apps
   az containerapp update \
     --name prepsmart-backend \
     --resource-group prepsmart-rg \
     --set-env-vars CLAUDE_API_KEY="new-key"
   ```

4. **Check git history**
   ```bash
   # If secret was committed, use BFG Repo-Cleaner or git filter-branch
   # Contact GitHub support if needed
   ```

---

## 📋 Deployment Checklist

Before deploying to production:

- [ ] All required secrets are set in GitHub
- [ ] Secrets are not in any `.env` files in the repo
- [ ] Pre-commit hooks are installed and working
- [ ] GitHub Actions security workflow passes
- [ ] Different API keys for production vs development
- [ ] Team members know how to rotate secrets
- [ ] Incident response plan for leaked secrets

---

## 🔗 Related Documentation

- [SECURITY.md](../SECURITY.md) - Security policy and vulnerability reporting
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [docs/QUICK_START.md](QUICK_START.md) - Local development setup
- [docs/PRODUCTION_URLS.md](PRODUCTION_URLS.md) - Production deployment

---

## 📞 Need Help?

- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Azure Service Principals**: https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal
- **Claude API**: https://docs.anthropic.com/claude/reference/getting-started-with-the-api

---

## 🎯 Quick Setup Script

```bash
#!/bin/bash
# setup-github-secrets.sh
# Run this locally to prepare secret values for GitHub

echo "Generating secrets for PrepSmart..."

# Generate Flask secret key
FLASK_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "FLASK_SECRET_KEY: $FLASK_SECRET"

# Get Claude API key
echo ""
echo "Get your Claude API key from: https://console.anthropic.com/"
echo "Then add it to GitHub Secrets as CLAUDE_API_KEY"

# Optional: Azure credentials
echo ""
echo "For Azure deployment, run:"
echo "az ad sp create-for-rbac --name 'prepsmart-github-actions' --role contributor --scopes /subscriptions/{sub-id}/resourceGroups/prepsmart-rg --sdk-auth"
```

Save this as `setup-github-secrets.sh`, make it executable with `chmod +x setup-github-secrets.sh`, then run it.

---

<div align="center">

**🔒 Remember: Secrets are called secrets for a reason. Keep them safe!**

</div>
