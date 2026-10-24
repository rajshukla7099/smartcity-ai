@echo off
echo ========================================================
echo   MultiCam AI - Public Internet Host (Localtunnel)
echo ========================================================
echo.
echo Your IP Password for verification: 115.248.83.149
echo (Anyone visiting the link enters this IP once to view the app)
echo.
echo Launching public tunnel on port 8501...
cmd /c npx --yes localtunnel --port 8501
pause
