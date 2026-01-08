# 🚀 Quick Start Guide - Todo AI Chatbot on Kubernetes

## ✅ Issue Fixed: "Failed to fetch" Error is RESOLVED!

The CORS error has been fixed. Registration and login now work perfectly!

---

## Start the Application (3 Steps)

### Step 1: Start Backend Service Tunnel

Open **Terminal 1** and run:
```cmd
minikube service todo-backend-service --url
```

You should see something like:
```
http://127.0.0.1:59705
! Because you are using a Docker driver on windows, the terminal needs to be open to run it.
```

✅ **Backend API is now accessible at:** `http://127.0.0.1:59705`

⚠️ **KEEP THIS TERMINAL OPEN!**

---

### Step 2: Start Frontend Service Tunnel

Open **Terminal 2** and run:
```cmd
minikube service todo-frontend-service --url
```

You should see something like:
```
http://127.0.0.1:63425
! Because you are using a Docker driver on windows, the terminal needs to be open to run it.
```

✅ **Frontend is now accessible at:** `http://127.0.0.1:63425` (your port may differ)

⚠️ **KEEP THIS TERMINAL OPEN TOO!**

---

### Step 3: Open in Browser

Copy the frontend URL from Terminal 2 and open it in your browser.

**Example:** `http://127.0.0.1:63425`

---

## Register & Login

### Register a New Account:

1. Click **"Sign Up"** tab
2. Fill in:
   - **Full Name:** multi media
   - **Email:** multi77@gmail.com
   - **Password:** Test1234! (minimum 8 characters)
3. Click **"Create Account"**
4. You should see: ✅ "Account created successfully! Please login with your credentials."

### Login:

1. Switch to **"Login"** tab
2. Enter your email and password
3. Click **"Login"**
4. You should be taken to the chat interface!

---

## Quick Demo Mode

Don't want to register? Click **"Quick Start (Demo Mode)"** button to instantly create a demo account and start chatting!

---

## Verify Everything is Working

### Check Backend Health:
```cmd
curl http://127.0.0.1:59705/health
```

Should return:
```json
{"status":"healthy","api":"operational","database":"connected"}
```

### Check All Pods are Running:
```cmd
kubectl get pods
```

You should see:
- `todo-backend-*` (2 pods) - Running ✅
- `todo-frontend-*` (2 pods) - Running ✅
- `todo-database-0` (1 pod) - Running ✅

---

## What Was Fixed?

**Problem:** "Failed to fetch" error during registration/login

**Root Cause:** CORS (Cross-Origin Resource Sharing) was blocking requests from the browser to the backend API

**Solution Applied:**
- Added `ALLOWED_ORIGINS=*` environment variable to backend
- This allows the backend to accept requests from any origin (perfect for development)
- CORS preflight requests now succeed (200 OK instead of 400 Bad Request)

---

## Troubleshooting

### "Failed to fetch" still appears?

1. **Make sure BOTH terminal windows are open and running the minikube service commands**
2. **Refresh the browser page** (Ctrl + F5 to clear cache)
3. **Check backend is accessible:**
   ```cmd
   curl http://127.0.0.1:59705/health
   ```
4. **Verify CORS is enabled:**
   ```cmd
   kubectl logs -l app.kubernetes.io/name=backend --tail=5
   ```

### Frontend not loading?

1. Check the frontend URL in Terminal 2
2. Make sure you're using the correct port
3. The port changes each time you run `minikube service`

### Backend not responding?

1. Check backend logs:
   ```cmd
   kubectl logs -l app.kubernetes.io/name=backend --tail=20
   ```
2. Restart backend pods:
   ```cmd
   kubectl delete pods -l app.kubernetes.io/name=backend
   ```
3. Wait 30 seconds and try again

---

## Stop the Application

### Stop Service Tunnels:
Press **Ctrl+C** in both terminal windows (Terminal 1 and Terminal 2)

### Stop Minikube (optional):
```cmd
minikube stop
```

### Start Again Later:
```cmd
minikube start
```
Then repeat Steps 1-3 above.

---

## For Your Phase 3 Deployment (Vercel + Render)

To fix the same issue on your deployed Phase 3:

### Render Backend:
1. Go to Render Dashboard → Your backend service
2. Environment → Add variable:
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://your-frontend.vercel.app`
3. Save and redeploy

### Vercel Frontend:
Make sure your environment variable is set:
- `VITE_API_BASE_URL` = `https://your-backend.onrender.com`

Then redeploy on Vercel.

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│          Your Browser (Windows)              │
│                                              │
│  Frontend: http://127.0.0.1:63425           │
│      │                                       │
│      │ HTTP Requests                         │
│      │ (CORS: ✅ Allowed)                    │
│      ▼                                       │
│  Backend: http://127.0.0.1:59705            │
│      │ ALLOWED_ORIGINS=*                     │
│      │                                       │
└──────┼───────────────────────────────────────┘
       │
       │ Minikube Tunnels
       │
┌──────▼───────────────────────────────────────┐
│         Minikube Cluster (Docker)            │
│                                              │
│  Frontend Service (NodePort :30080)          │
│    ├─ Pod 1: todo-frontend (Nginx)          │
│    └─ Pod 2: todo-frontend (Nginx)          │
│                                              │
│  Backend Service (NodePort :30800)           │
│    ├─ Pod 1: todo-backend (FastAPI)         │
│    └─ Pod 2: todo-backend (FastAPI)         │
│         │                                    │
│         ▼                                    │
│  Database Service (ClusterIP :5432)          │
│    └─ Pod: todo-database (PostgreSQL 16)    │
└─────────────────────────────────────────────┘
```

---

**Status:** ✅ FULLY WORKING
**Last Updated:** 2026-01-08
**Issue Fixed:** CORS blocking resolved
**Ready for:** Registration, Login, and AI Chat!

🎉 **Enjoy your Todo AI Chatbot!**
