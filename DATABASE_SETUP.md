# 🗄️ Database Setup Guide - Persistent Data Storage

## Problem
On Render.com's free tier, the filesystem is **ephemeral** - meaning:
- SQLite database files are **deleted** on restart/redeploy
- Uploaded images are **lost** on restart/redeploy
- Data does **not persist** between deployments

## Solution: PostgreSQL Database

We've updated the app to use **PostgreSQL** with **base64 image storage**. This means:
- ✅ Data persists permanently
- ✅ Images stored in database (no filesystem needed)
- ✅ Works on Render.com free tier
- ✅ Automatic backups included

## Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `satalert-db` (or your choice)
   - **Database**: `satalert` (or your choice)
   - **User**: Auto-generated
   - **Region**: Same as your web service (Oregon)
   - **Plan**: **Free** (90 days free, then $7/month) or **Starter** ($7/month)
4. Click **"Create Database"**
5. **Wait for database to be ready** (takes 1-2 minutes)

## Step 2: Connect Database to Web Service

1. Go to your **Web Service** (SatAlert)
2. Click on **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy from your PostgreSQL service
     - Go to your PostgreSQL service
     - Find **"Internal Database URL"** or **"Connection String"**
     - Copy the full URL (starts with `postgresql://...`)
5. Click **"Save Changes"**

## Step 3: Redeploy

1. Render will automatically redeploy when you save environment variables
2. Or manually trigger: **"Manual Deploy"** → **"Deploy latest commit"**
3. Wait for deployment to complete

## Step 4: Verify

1. Visit your website: `https://satalert.onrender.com`
2. Send a test alert from your Raspberry Pi
3. **Refresh the page** - data should persist!
4. **Redeploy** - data should still be there!

## How It Works

### Before (SQLite - Data Lost):
```
Alert → Save to database.db → Restart → ❌ Data deleted
```

### After (PostgreSQL - Data Persists):
```
Alert → Save to PostgreSQL → Restart → ✅ Data still there!
```

## Database Schema

The PostgreSQL table structure:

```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    image_data TEXT NOT NULL,        -- Base64 encoded image
    image_filename TEXT NOT NULL,     -- Original filename
    label TEXT NOT NULL,              -- "fire" or "smoke"
    confidence REAL NOT NULL,         -- 0.0 to 1.0
    timestamp TEXT NOT NULL           -- "YYYY-MM-DD HH:MM:SS"
);
```

## Local Development

For local development, the app will automatically use **SQLite** (no PostgreSQL needed):

```bash
# Run locally - uses SQLite
python app.py
```

When `DATABASE_URL` environment variable is set, it uses PostgreSQL.

## Troubleshooting

### Database Connection Error

1. **Check DATABASE_URL**:
   - Go to Render → PostgreSQL → Connection String
   - Verify it's set in Web Service environment variables

2. **Check Database Status**:
   - Ensure PostgreSQL service is running
   - Check if database is accessible

3. **Check Logs**:
   - Go to Web Service → Logs
   - Look for database connection errors

### Images Not Displaying

1. **Check image endpoint**: `/image/<alert_id>`
2. **Verify base64 encoding** in database
3. **Check browser console** for errors

### Data Still Not Persisting

1. **Verify DATABASE_URL** is set correctly
2. **Check app is using PostgreSQL**:
   - Look for "Using PostgreSQL" in logs
   - Or check database directly in Render dashboard

## Free Tier Limitations

- **PostgreSQL Free Tier**: 90 days free, then $7/month
- **PostgreSQL Starter**: $7/month (recommended for production)
- **Data Storage**: 1 GB free, then $0.25/GB/month

## Alternative: Render Persistent Disk (Paid)

If you prefer filesystem storage:

1. Upgrade to **Starter plan** ($7/month)
2. Add **Persistent Disk** in Web Service settings
3. Mount disk and store database/images there

**Note**: PostgreSQL solution is better because:
- ✅ Automatic backups
- ✅ Better performance
- ✅ No disk management needed
- ✅ Works on free tier (90 days)

## Migration from SQLite

If you have existing SQLite data:

1. Export data from SQLite
2. Import to PostgreSQL
3. Update DATABASE_URL
4. Redeploy

---

**Your data will now persist permanently! 🎉**
