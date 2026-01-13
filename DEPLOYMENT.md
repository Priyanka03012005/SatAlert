# 🚀 Deployment Guide - Render.com

## Step-by-Step Deployment Instructions

### Prerequisites
- GitHub account (or GitLab/Bitbucket)
- Render.com account (free tier available)

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - SatAlert"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `satalert`)
   - **DO NOT** initialize with README, .gitignore, or license

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/satalert.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render.com

1. **Sign Up/Login**:
   - Go to https://render.com
   - Sign up with GitHub (recommended) or email

2. **Create New Web Service**:
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub account (if not already connected)
   - Select your repository: `satalert`

3. **Configure Service**:
   - **Name**: `satalert` (or your choice)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Free` (or choose paid plan)

4. **Environment Variables**:
   - No environment variables needed!
   - The app automatically uses Render's `PORT` environment variable

5. **Click "Create Web Service"**

6. **Wait for Deployment**:
   - First deployment takes 5-10 minutes
   - Watch the build logs for any errors
   - Once deployed, you'll get a URL like: `https://wildfire-detection-alert.onrender.com`

### Step 3: Verify Deployment

1. **Check Homepage**:
   - Visit: `https://your-app.onrender.com`
   - Should show "No alerts detected yet"

2. **Check History Page**:
   - Visit: `https://your-app.onrender.com/history`
   - Should show empty state

3. **Test API Endpoint**:
   ```bash
   curl -X POST https://your-app.onrender.com/alert \
     -F "image=@test_image.jpg" \
     -F "label=fire" \
     -F "confidence=0.92" \
     -F "timestamp=2026-01-13 18:22:10"
   ```

### Step 4: Update AI Integration

Update your AI integration code to use the Render URL:

```python
ALERT_URL = "https://your-app.onrender.com/alert"
```

## ⚠️ Important Notes

### Free Tier Limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- Database and files persist between deployments
- 750 hours/month free (enough for testing)

### Production Considerations:
- For production, consider upgrading to a paid plan
- Database will persist, but consider using Render PostgreSQL for better reliability
- Images are stored in filesystem (persists on free tier)
- For high traffic, consider using S3 or similar for image storage

### Troubleshooting:

1. **Build Fails**:
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility

2. **App Crashes**:
   - Check logs in Render dashboard
   - Verify `app.py` uses `PORT` environment variable correctly

3. **Database Issues**:
   - Database auto-creates on first run
   - Check file permissions in Render logs

4. **Images Not Loading**:
   - Verify `static/alerts/` directory exists
   - Check file paths in database

## 📝 Post-Deployment Checklist

- [ ] Website loads successfully
- [ ] Homepage shows correctly
- [ ] History page works
- [ ] API endpoint accepts POST requests
- [ ] Test alert creation works
- [ ] Images display correctly
- [ ] Update AI integration URL

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- Flask Docs: https://flask.palletsprojects.com/

---

**Your app is now live! 🎉**
