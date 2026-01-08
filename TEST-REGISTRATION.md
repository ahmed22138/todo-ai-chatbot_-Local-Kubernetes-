# ✅ Registration Test - WORKING!

## Test the Fix NOW

### Prerequisites
Make sure you have TWO terminal windows running:

**Terminal 1 - Backend Tunnel:**
```cmd
minikube service todo-backend-service --url
```
Should show: `http://127.0.0.1:59705`

**Terminal 2 - Frontend Tunnel:**
```cmd
minikube service todo-frontend-service --url
```
Should show something like: `http://127.0.0.1:63425`

⚠️ **KEEP BOTH WINDOWS OPEN!**

## Registration Test

1. **Open your browser** to the frontend URL (from Terminal 2)

2. **Click "Sign Up" tab**

3. **Fill in the registration form:**
   - Full Name: `multi media`
   - Email: `multi77@gmail.com`
   - Password: `Test1234!` (minimum 8 characters)

4. **Click "Create Account"**

5. **Expected Result:** ✅ "Account created successfully! Please login with your credentials."

6. **Switch to Login tab** and login with the same credentials

## What Was Fixed

The error was **CORS blocking**. The backend was rejecting requests from your browser because the frontend URL wasn't in the allowed origins list.

**Fix Applied:**
- Backend now has `ALLOWED_ORIGINS=*` environment variable
- This allows requests from ANY origin (perfect for development)
- CORS preflight requests now return `200 OK` instead of `400 Bad Request`

## Verify CORS is Working

Open browser DevTools (F12) → Network tab:
1. Try registering
2. You should see:
   - `OPTIONS /api/auth/signup` → Status **200** ✅
   - `POST /api/auth/signup` → Status **201** ✅

**Before the fix:**
- `OPTIONS /api/auth/signup` → Status **400** ❌ (Disallowed CORS origin)

## Command Line Test

You can also test registration via command line:

```bash
curl -X POST http://127.0.0.1:59705/api/auth/signup \
  -H "Content-Type: application/json" \
  -H "Origin: http://127.0.0.1:63425" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "name": "New User"
  }'
```

Should return:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "...",
  "email": "newuser@example.com",
  "name": "New User"
}
```

## Troubleshooting

### Still seeing "Failed to fetch"?

1. **Check backend tunnel is running:**
   ```cmd
   netstat -ano | findstr :59705
   ```
   Should show a listening port.

2. **Check frontend can reach backend:**
   ```cmd
   curl http://127.0.0.1:59705/health
   ```
   Should return: `{"status":"healthy","api":"operational","database":"connected"}`

3. **Check CORS in backend pod:**
   ```bash
   kubectl get pods -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}' | xargs kubectl exec -- env | grep ALLOWED_ORIGINS
   ```
   Should show: `ALLOWED_ORIGINS=*`

4. **Restart browser** - Clear cache with Ctrl+Shift+Delete

5. **Check browser console (F12)** for detailed error messages

## For Phase 3 (Vercel/Render)

To fix the same issue on your deployed Phase 3:

### On Render (Backend):
1. Go to your backend service
2. Environment → Add variable:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** `https://your-app.vercel.app`
3. Click "Save"
4. Render will auto-redeploy

### On Vercel (Frontend):
Make sure `.env.production` has:
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

Then redeploy:
```bash
git add .
git commit -m "Fix backend URL"
git push
```

---

**Status:** ✅ FIXED AND TESTED
**Error:** "Failed to fetch" during registration
**Cause:** CORS blocking requests from browser
**Solution:** Set `ALLOWED_ORIGINS=*` in backend deployment
**Date:** 2026-01-08
