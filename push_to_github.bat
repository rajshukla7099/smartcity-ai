@echo off
setlocal
echo ========================================================
echo   MultiCam AI - Push to GitHub
echo ========================================================

set GIT_EXE="C:\Users\rajsh\AppData\Local\GitHubDesktop\app-3.6.7\resources\app\git\cmd\git.exe"

set /p REPO_URL="Enter your GitHub Repository URL (or press Enter for default: https://github.com/rajshukla7099/smartcity-ai.git): "
if "%REPO_URL%"=="" set REPO_URL=https://github.com/rajshukla7099/smartcity-ai.git

echo.
echo Setting remote origin to: %REPO_URL%
%GIT_EXE% remote remove origin >nul 2>&1
%GIT_EXE% remote add origin %REPO_URL%

echo.
echo Pushing branch 'main' to GitHub...
%GIT_EXE% push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! All files uploaded to GitHub successfully!
    echo ========================================================
) else (
    echo.
    echo [!] Push failed. Please make sure:
    echo     1. You created the repository on https://github.com/new
    echo     2. The repository name matches the URL.
)

pause
