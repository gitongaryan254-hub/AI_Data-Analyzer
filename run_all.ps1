param(
    [switch]$SkipStreamlit,
    [switch]$MseOnly,
    [switch]$SkipMlCli
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workDir = Join-Path $projectRoot "data cleaning and vitualization"

if (-not (Test-Path $workDir)) {
    throw "Project folder not found: $workDir"
}

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = "python"
}

Write-Host "Using Python: $pythonExe"
Write-Host "Working directory: $workDir"

Push-Location $workDir

try {
    if ($MseOnly) {
        Write-Host "[MSE] Calculating Mean Squared Error..."
        & $pythonExe "machinelearning_model.py" --mse-only
        if ($LASTEXITCODE -ne 0) { throw "MSE step failed." }
        Write-Host "Done."
        exit 0
    }

    Write-Host "[1/4] Cleaning data..."
    & $pythonExe "clean_csv.py"
    if ($LASTEXITCODE -ne 0) { throw "Data cleaning failed." }

    Write-Host "[2/4] Generating bar chart..."
    & $pythonExe "visualize_data.py"
    if ($LASTEXITCODE -ne 0) { throw "Visualization failed." }

    Write-Host "[3/4] Generating HTML profile report..."
    & $pythonExe "profile_cleaned_csv_basic.py"
    if ($LASTEXITCODE -ne 0) { throw "Profiling failed." }

    Write-Host "[4/4] Calculating MSE..."
    & $pythonExe "machinelearning_model.py" --mse-only
    if ($LASTEXITCODE -ne 0) { throw "MSE step failed." }

    if (-not $SkipStreamlit) {
        Write-Host "Starting Streamlit in a new terminal window on http://localhost:8501 ..."
        $streamlitCommand = "Set-Location `"$projectRoot`"; & `"$pythonExe`" -m streamlit run `"data cleaning and vitualization\streamlit_app.py`""
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $streamlitCommand | Out-Null
        Write-Host "Streamlit launched."
    }

    if ((-not $SkipMlCli) -and (-not $SkipStreamlit)) {
        Write-Host "Starting terminal ML predictor interface..."
        & $pythonExe "machinelearning_model.py"
        exit $LASTEXITCODE
    }

    Write-Host "All non-interactive steps completed successfully."
}
finally {
    if ((Get-Location).Path -eq $workDir) {
        Pop-Location
    }
}
