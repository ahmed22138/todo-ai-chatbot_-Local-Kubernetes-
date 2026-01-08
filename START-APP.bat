@echo off
echo ========================================
echo Todo AI Chatbot - Starting Services
echo ========================================
echo.

echo Starting Minikube service tunnels...
echo.

echo [1/3] Starting backend service tunnel (port 30800)...
start "Backend Service" cmd /k "minikube service todo-backend-service --url && echo Backend running. Keep this window open!"

timeout /t 3 /nobreak >nul

echo [2/3] Starting frontend service tunnel (port 30080)...
start "Frontend Service" cmd /k "minikube service todo-frontend-service --url && echo Frontend running. Keep this window open!"

timeout /t 5 /nobreak >nul

echo [3/3] Opening application in browser...
start http://127.0.0.1:63146

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Frontend: http://127.0.0.1:63146 (approximate - check Frontend Service window)
echo Backend:  http://127.0.0.1:30800 (approximate - check Backend Service window)
echo.
echo IMPORTANT: Keep both service windows open while using the app!
echo.
echo Press any key to view pod status...
pause >nul

kubectl get pods
echo.
echo Press any key to exit (services will keep running)...
pause >nul
