@echo off
echo ========================================
echo    ETL Engine Test Script
echo ========================================
echo.
echo This script will test if your ETL Engine is working correctly.
echo Make sure the ETL Engine is running first (python run.py)
echo.
pause
echo.
echo Running tests...
echo.
python test_etl_engine.py
echo.
echo Test completed!
echo.
pause
