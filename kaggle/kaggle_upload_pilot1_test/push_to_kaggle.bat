@echo off
setlocal
REM Push the Pilot 1 TEST notebook to Kaggle.
REM Set KAGGLE_USERNAME and KAGGLE_KEY before running, and update
REM kernel-metadata.json with your real Kaggle username.

if "%KAGGLE_USERNAME%"=="" (
  echo ERROR: Set KAGGLE_USERNAME environment variable.
  exit /b 1
)
if "%KAGGLE_KEY%"=="" (
  echo ERROR: Set KAGGLE_KEY environment variable.
  exit /b 1
)

python -m pip install --quiet kaggle
kaggle kernels push -p .
