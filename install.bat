@echo off
setlocal EnableDelayedExpansion

echo Setting up virtual environment and installing dependencies for JARVIS...

where python3.11 >nul 2>&1
if %errorlevel% neq 0 ( 
    echo Python 3.11 not found. Please ensure Python 3.11 is installed and added to PATH.
    pause
    exit /b 1
)

where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found. Please ensure pip is installed with Python.
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
echo Creating Python virtual environment in %SCRIPT_DIR%jarvis_venv...
python3.11 -m venv "%SCRIPT_DIR%jarvis_venv"
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Please check your Python installation.
    pause
    exit /b 1
)

echo Activating virtual environment...
cd "%SCRIPT_DIR%jarvis_venv"
call jarvis_venv\Scripts\activate

python -m pip install --upgrade pip

pip install pyaudio faster-whisper==1.1.1 ollama chatterbox-tts

SET /P GPU_SUPPORT=Do you want to enable GPU support for CUDA? (yes/no): 

SET "GPU_SUPPORT=%GPU_SUPPORT:~0,1%"
IF /I "%GPU_SUPPORT%"=="y" (
    ECHO Installing PyTorch with CUDA support...
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
) ELSE (
    ECHO Installing PyTorch without CUDA support...
    pip3 install torch torchvision torchaudio
)

if %errorlevel% neq 0 (
    echo Failed to install some Python packages. Please check your internet connection or pip configuration.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not found. Please download and install Ollama from https://ollama.com and add it to PATH.
    pause
    exit /b 1
)

echo Pulling gemma3:4b model for Ollama...
ollama pull gemma3:4b
if %errorlevel% neq 0 (
    echo Failed to pull gemma3:4b model. Please ensure Ollama is running and try again.
    pause
    exit /b 1
)

echo Deactivating virtual environment...
deactivate

echo.
echo Installation complete! A virtual environment has been created in 'jarvis_venv'.
echo To run JARVIS, activate the virtual environment with 'jarvis_venv\Scripts\activate' and then run 'python jarvis.py'.
echo.

pause
endlocal
exit /b 0