@echo off
setlocal EnableDelayedExpansion

echo Setting up Conda environment and installing dependencies for JARVIS...

where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo Conda not found. Please install Anaconda or Miniconda and ensure 'conda' is added to your PATH.
    pause
    exit /b 1
)

:: Set environment name
set "ENV_NAME=jarvis_env"

echo Creating Conda environment '%ENV_NAME%' with Python 3.11...
conda create -y -n %ENV_NAME% python=3.11
if %errorlevel% neq 0 (
    echo Failed to create Conda environment. Please check your Conda installation.
    pause
    exit /b 1
)

echo Activating Conda environment...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo Failed to activate Conda environment.
    pause
    exit /b 1
)

:: Upgrade pip and install packages
python -m pip install --upgrade pip

echo Installing required Python packages...
pip install pyaudio faster-whisper==1.1.1 ollama chatterbox-tts

:: Ask about GPU support
SET /P GPU_SUPPORT=Do you want to enable GPU support for CUDA? (yes/no): 
SET "GPU_SUPPORT=%GPU_SUPPORT:~0,1%"

IF /I "%GPU_SUPPORT%"=="y" (
    ECHO Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
) ELSE (
    ECHO Installing PyTorch without CUDA support...
    pip install torch torchvision torchaudio
)

if %errorlevel% neq 0 (
    echo Failed to install Python packages. Please check your internet connection or pip configuration.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not found. Please install it from https://ollama.com and ensure it is added to your PATH.
    pause
    exit /b 1
)

echo Pulling gemma3:4b model for Ollama...
ollama pull gemma3:4b
if %errorlevel% neq 0 (
    echo Failed to pull gemma3:4b model. Ensure Ollama is running and try again.
    pause
    exit /b 1
)

echo.
echo Installation complete! The Conda environment '%ENV_NAME%' is ready.
echo To activate it, run: conda activate %ENV_NAME%
echo Then run 'python jarvis.py' to start JARVIS.
echo.

pause
endlocal
exit /b 0
:: End of install.bat
:: This script sets up a Conda environment, installs necessary packages, and configures JARVIS for use.