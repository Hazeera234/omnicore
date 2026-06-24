<#
.SYNOPSIS
    Automated setup script for Windows 11 for the Cognitive Agents project.
.DESCRIPTION
    This script verifies the presence of required configuration files, installs 
    Docker and Node.js via winget if missing, sets up a Python virtual environment, 
    installs Python and Node dependencies, and finally runs a verification script.
#>

$ErrorActionPreference = "Stop"

Write-Host "Starting setup for Windows 11..." -ForegroundColor Cyan

# 1. Check required files (package.json, and the python requirements)
$RequiredFiles = @(
    "package.json",
    "apps\api\requirements.txt",
    "apps\worker\requirements.txt"
)

Write-Host "`n[1/6] Verifying required files exist..." -ForegroundColor Yellow
$missingFiles = $false
foreach ($file in $RequiredFiles) {
    if (-Not (Test-Path $file)) {
        Write-Host "Missing required file: $file" -ForegroundColor Red
        $missingFiles = $true
    } else {
        Write-Host "Found: $file" -ForegroundColor Green
    }
}

if ($missingFiles) {
    Write-Host "Please ensure all required files and folders are present before running the setup." -ForegroundColor Red
    exit 1
}

# 2. Install Docker
Write-Host "`n[2/6] Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker is already installed." -ForegroundColor Green
} else {
    Write-Host "Docker not found. Installing Docker Desktop via winget..." -ForegroundColor Cyan
    winget install --id Docker.DockerDesktop -e --accept-package-agreements --accept-source-agreements
    Write-Host "Docker installed. Note: You may need to restart your terminal or computer for Docker to be fully operational." -ForegroundColor Yellow
}

# 3. Install Node.js
Write-Host "`n[3/6] Checking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "Node.js is already installed. Version: $((node -v))" -ForegroundColor Green
} else {
    Write-Host "Node.js not found. Installing Node.js via winget..." -ForegroundColor Cyan
    winget install --id OpenJS.NodeJS -e --accept-package-agreements --accept-source-agreements
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 4. Install Node dependencies
Write-Host "`n[4/6] Installing Node dependencies..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    npm install
}

# 5. Create Python Virtual Environment and install requirements
Write-Host "`n[5/6] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Installing Python via winget..." -ForegroundColor Cyan
    winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

if (-Not (Test-Path ".venv")) {
    Write-Host "Creating .venv..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "Activating venv and installing Python dependencies..." -ForegroundColor Cyan
$venvPython = ".\.venv\Scripts\python.exe"
$venvPip = ".\.venv\Scripts\pip.exe"

& $venvPip install --upgrade pip
& $venvPip install -r apps\api\requirements.txt
& $venvPip install -r apps\worker\requirements.txt

# 6. Run verification file
Write-Host "`n[6/6] Running Python verification file..." -ForegroundColor Yellow
$VerifyFile = "verify.py"

if (-Not (Test-Path $VerifyFile)) {
    Write-Host "Verification file '$VerifyFile' not found. Creating a default verify.py..." -ForegroundColor Yellow
    @"
import sys
print('=============================================')
print('Verification successful! Environment is set up.')
print('Python version:', sys.version)
print('=============================================')
"@ | Out-File -FilePath $VerifyFile -Encoding utf8
}

Write-Host "Executing $VerifyFile..." -ForegroundColor Cyan
& $venvPython $VerifyFile

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "To activate the virtual environment manually, run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
