# PrepSmart - Production URLs

**Deployed on**: Azure Container Apps
**Region**: East US
**Status**: ✅ LIVE

---

## 🌐 URLs

### Main Application
```
https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io
```
**Use this for demos and sharing**

### Backend API
```
https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io
```

### Debug Viewer
```
https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/debug-viewer
```
**Show this to demonstrate technical sophistication**

---

## 🔗 API Endpoints

### Health Check
```
GET https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/health
```

### Start Crisis Plan
```
POST https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/start
```

### Check Status
```
GET https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/{task_id}/status
```

### Get Results
```
GET https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/{task_id}/result
```

### Debug (NEW)
```
GET https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/{task_id}/debug
```

### Download PDF
```
GET https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/{task_id}/pdf
```

---

## ✅ Health Check (Just Verified)

**Backend Status**: ✅ Healthy
```json
{
    "status": "healthy",
    "dependencies": {
        "claude_api": "up",
        "database": "up"
    },
    "timestamp": "2025-10-31T05:36:33Z"
}
```

**Frontend Status**: ✅ Running (HTTP 200)

---

## 🎯 For Demo

### Short URL for Sharing
Use the frontend URL:
```
https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io
```

### QR Code (Optional)
Generate a QR code pointing to the frontend URL for easy mobile access during demo.

### Demo Flow
1. Open frontend URL in browser
2. Select crisis type
3. Fill questionnaire
4. Show agent dashboard
5. View results
6. **Bonus**: Show debug viewer with task_id

---

## 🔧 Troubleshooting Production

### Check if backend is responsive
```bash
curl https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/health
```

### Check if frontend loads
```bash
curl -I https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io
```

### View logs
```bash
# Backend logs
az containerapp logs show --name prepsmart-backend --resource-group prepsmart-rg --tail 50

# Frontend logs
az containerapp logs show --name prepsmart-frontend --resource-group prepsmart-rg --tail 50
```

### Restart if needed
```bash
# Restart backend
az containerapp update --name prepsmart-backend --resource-group prepsmart-rg

# Restart frontend
az containerapp update --name prepsmart-frontend --resource-group prepsmart-rg
```

---

## 📊 Production Test

### Quick Test (30 seconds)
```bash
# 1. Create a plan
TASK_ID=$(curl -s -X POST https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/start \
  -H "Content-Type: application/json" \
  -d '{
    "crisis_mode": "natural_disaster",
    "specific_threat": "hurricane",
    "location": {"city": "Miami", "state": "FL"},
    "household": {"adults": 2, "children": 1},
    "housing_type": "apartment",
    "budget_tier": 100
  }' | python -m json.tool | grep task_id | cut -d'"' -f4)

echo "Task ID: $TASK_ID"

# 2. Wait 90 seconds
sleep 90

# 3. Check results
curl -s https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api/crisis/$TASK_ID/result | python -m json.tool | head -50
```

---

## 🎁 For Submission

### Include these URLs in your submission:
- **Live App**: https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io
- **Debug Viewer**: https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/debug-viewer
- **GitHub Repo**: (your repo URL)
- **Demo Video**: (if you make one)

### Test Before Submitting
- [ ] Frontend loads
- [ ] Can select crisis type
- [ ] Can fill questionnaire
- [ ] Agents execute
- [ ] Results display
- [ ] PDF downloads
- [ ] Debug viewer works

---

## 🚀 Deployment Info

**Platform**: Azure Container Apps
**Resource Group**: `prepsmart-rg`
**Region**: `eastus`
**Containers**:
- `prepsmart-backend` - Python/Flask API
- `prepsmart-frontend` - Static HTML/CSS/JS

**Environment Variables** (Backend):
- `CLAUDE_API_KEY` - Set ✅
- `DATABASE_URL` - SQLite (ephemeral, resets on restart)
- `FLASK_ENV` - production
- `FLASK_SECRET_KEY` - Set ✅

**Note**: Database is ephemeral (in-container). All data lost on restart. For production persistence, use Azure Database for PostgreSQL.

---

## 📞 Quick Reference

**Main URL**: `https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io`

**Debug URL**: `https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/debug-viewer`

**Status**: ✅ Both verified working (2025-10-31 05:36 UTC)

---

**You're live! Share this URL for your hackathon submission.** 🎉
