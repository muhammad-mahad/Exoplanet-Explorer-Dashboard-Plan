@echo off
REM Batch script to set up and run the Exoplanet Explorer Dashboard

REM Set the title of the command prompt window
TITLE Exoplanet Explorer Setup & Run

echo ============================================================
echo  Setting up and Running Exoplanet Explorer Dashboard
echo ============================================================
echo.

REM Check if Python is available (basic check by trying to get version)
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python does not seem to be installed or is not in your PATH.
    echo Please install Python and ensure it's added to your PATH.
    goto :eof
)

REM --- Step 1: Check and Create Virtual Environment ---
echo [STEP 1/4] Checking for virtual environment (venv)...
IF NOT EXIST venv (
    echo Virtual environment 'venv' not found. Creating it now...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo ERROR: Failed to create virtual environment. Please check your Python installation.
        goto :error
    )
    echo Virtual environment created successfully.
) ELSE (
    echo Virtual environment 'venv' already exists.
)
echo.

REM --- Step 2: Activate Virtual Environment ---
echo [STEP 2/4] Activating virtual environment...
IF NOT EXIST venv\Scripts\activate.bat (
    echo ERROR: venv\Scripts\activate.bat not found. Cannot activate virtual environment.
    goto :error
)
CALL venv\Scripts\activate.bat
IF ERRORLEVEL 1 (
    echo ERROR: Failed to activate virtual environment.
    goto :error
)
echo Virtual environment activated.
echo.

REM --- Step 3: Install Requirements ---
echo [STEP 3/4] Installing required packages from requirements.txt...
IF NOT EXIST requirements.txt (
    echo WARNING: requirements.txt not found. Skipping package installation.
    echo Please ensure requirements.txt is present if packages are needed.
) ELSE (
    pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo ERROR: Failed to install packages from requirements.txt.
        echo Please check the file and your internet connection.
        goto :error
    )
    echo Packages installed successfully.
)
echo.

REM --- Step 4: Run Streamlit App ---
echo [STEP 4/4] Starting Streamlit application (Dashboard.py)...
IF NOT EXIST Dashboard.py (
    echo ERROR: Dashboard.py not found. Cannot start the application.
    goto :error
)

streamlit run Dashboard.py
IF ERRORLEVEL 1 (
    echo ERROR: Failed to start Streamlit application.
    echo Ensure Streamlit is installed correctly (it should be in requirements.txt).
    goto :error
)

echo.
echo Streamlit application started. Closing this script window will stop the app.
goto :success

:error
echo.
echo ============================================================
echo  An error occurred. Please check the messages above.
echo ============================================================
pause
goto :eof

:success
echo.
echo ============================================================
echo  Setup complete. The application should now be running.
echo ============================================================
REM The script will end here, but Streamlit will keep running.
REM Add a pause if you want the window to stay open after Streamlit is launched from here,
REM but usually, Streamlit takes over the console.
REM pause
goto :eof

:eof
REM End of file
