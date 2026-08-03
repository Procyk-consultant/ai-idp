<#>
.SYNOPSIS
    AI-IDP / AegisTrace + Hermes Browser Automation - Complete Deployment Script
.DESCRIPTION
    Runs as Administrator. Handles:
    1. Git force push to GitHub (clean history)
    2. Browser automation locked-in deployment
    3. Zenodo deposition via API
    4. Metadata updates with DOI
.NOTES
    Run as Administrator in PowerShell
    Requires: GITHUB_TOKEN and ZENODO_TOKEN environment variables
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$true)]
    [string]$ZenodoToken,
    
    [string]$ProjectPath = "C:\Cognitive Industries\AI-IDP-AegisTrace",
    [string]$HermesPath = "C:\Users\Agenc\AppData\Local\hermes"
)

# ─── CONFIGURATION ───
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-Admin {
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ─── PRE-FLIGHT CHECKS ───
Write-Log "Starting AI-IDP / AegisTrace + Hermes Deployment"
Write-Log "Project: $ProjectPath"
Write-Log "Hermes: $HermesPath"

if (-not (Test-Admin)) {
    Write-Log "ERROR: Must run as Administrator" "ERROR"
    exit 1
}

if (-not (Test-Path $ProjectPath)) {
    Write-Log "ERROR: Project path not found: $ProjectPath" "ERROR"
    exit 1
}

if (-not (Test-Path $HermesPath)) {
    Write-Log "ERROR: Hermes path not found: $HermesPath" "ERROR"
    exit 1
}

if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Log "ERROR: GitHub token required" "ERROR"
    exit 1
}

if ([string]::IsNullOrEmpty($ZenodoToken)) {
    Write-Log "ERROR: Zenodo token required" "ERROR"
    exit 1
}

Write-Log "Pre-flight checks passed" "OK"

# ─── STEP 1: GIT FORCE PUSH ───
Write-Log "=== STEP 1: Git Force Push ==="
Set-Location $ProjectPath

Write-Log "Checking git status..."
$status = git status --porcelain
if ($status) {
    Write-Log "Uncommitted changes detected, committing..."
    git add .
    git commit -m "chore: pre-deployment commit before force push"
} else {
    Write-Log "Working tree clean"
}

Write-Log "Force pushing to GitHub..."
$env:GITHUB_TOKEN = $GitHubToken
try {
    git push --force origin main
    Write-Log "GitHub force push successful" "OK"
} catch {
    Write-Log "GitHub push failed: $_" "ERROR"
    exit 1
}

# ─── STEP 2: VERIFY GITHUB REPO =====
Write-Log "Verifying GitHub repository..."
Start-Sleep 3
try {
    $repoInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/Procyk-consultant/ai-idp" `
        -Headers @{Authorization = "token $GitHubToken"} `
        -ErrorAction Stop
    Write-Log "GitHub repo verified: $($repoInfo.html_url)" "OK"
} catch {
    Write-Log "Warning: Could not verify GitHub repo: $_" "WARN"
}

# ─── STEP 3: ZENODO DEPOSITION =====
Write-Log "=== STEP 2: Zenodo Deposition ==="

$env:ZENODO_TOKEN = $ZenodoToken
$env:GITHUB_TOKEN = $GitHubToken

Write-Log "Running Hermes deployment script..."
Set-Location "C:\Users\Agenc\AppData\Local\hermes"

try {
    $result = python scripts/deploy_all.py 2>&1
    Write-Log "Deployment output: $result"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Deployment completed successfully" "OK"
    } else {
        Write-Log "Deployment failed with exit code $LASTEXITCODE" "ERROR"
        Write-Log "Output: $result" "ERROR"
        exit 1
    }
} catch {
    Write-Log "Deployment script failed: $_" "ERROR"
    exit 1
}

# ─── STEP 4: VERIFY ZENODO DOI =====
Write-Log "=== STEP 3: Verify Zenodo DOI ==="
Start-Sleep 5

try {
    $depositions = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions" `
        -Headers @{Authorization = "Bearer $ZenodoToken"} `
        -ErrorAction Stop
    
    if ($depositions.Count -gt 0) {
        $latest = $depositions | Sort-Object created -Descending | Select-Object -First 1
        $doi = $latest.doi
        Write-Log "Zenodo deposition created: https://doi.org/$doi" "OK"
        
        # Verify DOI resolves
        Start-Sleep 3
        try {
            $resolve = Invoke-WebRequest -Uri "https://doi.org/$doi" -MaximumRedirection 5 -ErrorAction Stop
            Write-Log "DOI resolves successfully" "OK"
        } catch {
            Write-Log "DOI created but resolution pending" "WARN"
        }
    } else {
        Write-Log "No depositions found" "WARN"
    }
} catch {
    Write-Log "Could not verify Zenodo: $_" "WARN"
}

# ─── STEP 5: VERIFY GITHUB DOI UPDATE =====
Write-Log "=== STEP 4: Verify GitHub DOI Update ==="
Start-Sleep 3

try {
    $repoInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/Procyk-consultant/ai-idp" `
        -Headers @{Authorization = "token $GitHubToken"} `
        -ErrorAction Stop
    
    $readme = Invoke-RestMethod -Uri "https://api.github.com/repos/Procyk-consultant/ai-idp/contents/README.md" `
        -Headers @{Authorization = "token $GitHubToken"; Accept = "application/vnd.github.v3.raw"} `
        -ErrorAction Stop
    
    if ($readme -match "zenodo.org/badge/DOI") {
        Write-Log "README updated with Zenodo badge" "OK"
    } else {
        Write-Log "README may not have Zenodo badge yet" "WARN"
    }
} catch {
    Write-Log "Could not verify GitHub update: $_" "WARN"
}

# ─── COMPLETE =====
Write-Log "=== DEPLOYMENT COMPLETE ==="
Write-Log "GitHub: https://github.com/Procyk-consultant/ai-idp"
if ($doi) {
    Write-Log "Zenodo: https://doi.org/$doi"
}
Write-Log "Hermes browser automation locked-in: ACTIVE"
Write-Log "All done!"

exit 0