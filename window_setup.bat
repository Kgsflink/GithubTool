@echo off
REM -------------------------------------------------
REM Script to download github.exe, create config.json, and set environment path
REM -------------------------------------------------

REM Define variables
set "URL=https://raw.githubusercontent.com/Kgsflink/GithubTool/main/dist/github.exe"
set "DEST_DIR=%ProgramFiles%\GithubTool"
set "EXE_FILE=%DEST_DIR%\github.exe"
set "CONFIG_FILE=%DEST_DIR%\config.json"

REM Create the destination directory if it doesn't exist
if not exist "%DEST_DIR%" (
    echo Creating directory: %DEST_DIR%
    mkdir "%DEST_DIR%"
) else (
    echo Directory %DEST_DIR% already exists.
)

REM Download the executable using PowerShell
echo Downloading github.exe to %EXE_FILE%
powershell -Command "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%EXE_FILE%' -UseBasicParsing } catch { Write-Error 'Download failed: $_'; exit 1 }"

REM Check if the download was successful
if exist "%EXE_FILE%" (
    echo Download successful: %EXE_FILE%
) else (
    echo ERROR: Failed to download github.exe. Exiting script.
    pause
    exit /b 1
)

REM Create the config.json file with default content
if not exist "%CONFIG_FILE%" (
    echo Creating config.json file...
    echo { > "%CONFIG_FILE%"
    echo     "github_token": "your_github_api_token_here" >> "%CONFIG_FILE%"
    echo } >> "%CONFIG_FILE%"
    echo config.json created successfully at %CONFIG_FILE%.
) else (
    echo config.json already exists. Skipping creation.
)

REM Add the folder to the system PATH (requires admin privileges)
echo Adding %DEST_DIR% to the system PATH...
for %%x in ("%DEST_DIR%") do (
    set "NEW_PATH=%%~x"
)

setx /M PATH "%PATH%;%NEW_PATH%" > nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to update PATH. Run this script as Administrator.
    pause
    exit /b 1
)

REM Verify the installation
where github.exe > nul 2>&1
if errorlevel 0 (
    echo github.exe is now accessible from the command line.
) else (
    echo ERROR: github.exe could not be found in the PATH. Check the setup.
    pause
    exit /b 1
)

echo Script completed successfully. Restart the command prompt to use github.exe.
pause
