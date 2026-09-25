@echo off
setlocal

echo ==========================================
echo AIVI Deliverable 03 - Gemini API Setup
echo ==========================================
echo.

if exist .env (
    echo .env already exists. Skipping API key creation.
) else (
    echo Enter your Gemini API key below.
    echo The key will be saved ONLY in the local .env file.
    echo It is ignored by Git and will NOT be uploaded.
    echo.
    set /p GEMINI_API_KEY=Gemini API key: 
    >.env echo GEMINI_API_KEY=%GEMINI_API_KEY%
    >>.env echo GEMINI_MODEL=gemini-2.5-flash
    echo.
    echo Local .env created successfully.
)

echo.
echo Installing/updating dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Running the live Gemini demo...
python main.py --resume-file samples/resume.txt --jd-file samples/job_description.txt
if errorlevel 1 goto :error

echo.
echo ==========================================
echo LIVE GEMINI TEST COMPLETED
echo ==========================================
pause
exit /b 0

:error
echo.
echo Something failed. Read the error above.
pause
exit /b 1
