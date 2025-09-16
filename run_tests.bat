@echo off
echo ========================================
echo    ETL Engine API Testing Suite
echo ========================================
echo.
echo This will help you test the ETL Engine API
echo.
echo Step 1: Make sure the ETL Engine is running
echo        (python run.py in another terminal)
echo.
pause
echo.
echo Step 2: Running automated tests...
echo.
python test_etl_engine.py
echo.
echo Step 3: Test completed!
echo.
echo Next steps:
echo 1. Visit http://localhost:8001/docs for interactive testing
echo 2. Use the JSON files in this folder for API requests
echo 3. Check storage/transformed/ for output files
echo.
pause
