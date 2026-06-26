# 🚀 Deployment Guide — Step by Step

## Requirements
- GitHub account (free) → https://github.com
- Railway account (free) → https://railway.app

---

## Step 1 — Upload Project to GitHub

### Open PowerShell in project folder and run:

```powershell
git init
git add .
git commit -m "first commit"
```

### Create a new repository on GitHub:
1. Open https://github.com/new
2. Enter repository name: `english-platform`
3. Make it **Private**
4. Click **Create repository**

### Upload the code:
```powershell
git remote add origin https://github.com/USERNAME/english-platform.git
git branch -M main
git push -u origin main
```
> Replace USERNAME with your GitHub username

---

## Step 2 — Create Project on Railway

1. Open https://railway.app
2. Sign in with GitHub
3. Click **New Project**
4. Choose **Deploy from GitHub repo**
5. Select `english-platform` repository
6. Build will start automatically ✅

---

## Step 3 — Add PostgreSQL Database

1. In Railway dashboard, click **+ New**
2. Choose **Database → Add PostgreSQL**
3. Wait a minute for the database to be created ✅

---

## Step 4 — Link Environment Variables

1. Click on your service (not the database)
2. Go to **Variables**
3. Click **+ New Variable** and add:

| Variable | Value |
|---------|--------|
| `SECRET_KEY` | Any long random text like: `my-super-secret-key-12345-english` |
| `DATABASE_URL` | Copy from database automatically (see below) |

### How to copy DATABASE_URL:
1. Click on PostgreSQL service
2. Click **Connect**
3. Copy **DATABASE_URL** value
4. Paste it in your service variables

---

## Step 5 — Get the URL

1. Click on your service
2. Click **Settings**
3. Under **Domains** click **Generate Domain**
4. You'll get a URL like: `https://english-platform-production.up.railway.app` 🎉

---

## ✅ Login Credentials After Deployment

| Role | Email | Password |
|-------|--------|-------------|
| 👨‍🏫 Teacher | teacher@english.com | teacher123 |
| 👤 Student | Create new account | — |

> **Important:** Change the teacher password from the dashboard after first login!

---

## 🔄 How to Upload Updates Later

```powershell
git add .
git commit -m "description of changes"
git push
```
Railway will redeploy automatically within a minute ✅

---

## ❓ Common Issues

**Project not working after deployment:**
- Check **Logs** in Railway
- Make sure DATABASE_URL is set correctly

**Images not showing after redeploy:**
- Railway doesn't persist uploaded files between deployments
- Solution: Use **Cloudinary** for image storage (free) — see README

**Error 500:**
- Open Logs in Railway and look for the red line