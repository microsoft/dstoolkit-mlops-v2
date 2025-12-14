# Test script for model discovery logic
# Run this locally to verify before running the workflow

param(
    [string]$ModelType = "nyc_taxi",
    [string]$SubscriptionId = "310ab569-9762-484e-8ce9-a650803297ea",
    [string]$ResourceGroup = "rg_modelfactory",
    [string]$WorkspaceName = "mfaml001"
)

Write-Host "=== Testing Model Discovery ===" -ForegroundColor Cyan
Write-Host "Model Type: $ModelType"
Write-Host ""

Write-Host "Step 1: Discovering unique model names with prefix '$ModelType'" -ForegroundColor Yellow
$uniqueNames = az ml model list `
    --resource-group $ResourceGroup `
    --workspace-name $WorkspaceName `
    --subscription $SubscriptionId `
    --query "[?starts_with(name, '$ModelType')].name" `
    -o json | ConvertFrom-Json | Select-Object -Unique

Write-Host "Found model names: $($uniqueNames -join ', ')"

Write-Host ""
Write-Host "Step 2: Getting latest version for each model" -ForegroundColor Yellow
$allModels = @()
foreach ($modelName in $uniqueNames) {
    Write-Host "  Checking: $modelName"
    $versions = az ml model list `
        --name $modelName `
        --resource-group $ResourceGroup `
        --workspace-name $WorkspaceName `
        --subscription $SubscriptionId `
        --query "[].{name:name, version:version, created:creation_context.created_at}" `
        -o json | ConvertFrom-Json

    if ($versions) {
        $latest = $versions | Sort-Object -Property created -Descending | Select-Object -First 1
        $allModels += $latest
        Write-Host "    Latest version: $($latest.version) (created: $($latest.created))"
    }
}

$allModels | Format-Table name, version, created

Write-Host ""
Write-Host "Step 3: Selecting most recently created model" -ForegroundColor Yellow
$latestModel = $allModels | Sort-Object -Property created -Descending | Select-Object -First 1

if (-not $latestModel) {
    Write-Host "ERROR: No models found" -ForegroundColor Red
    exit 1
}

$MODEL_NAME = $latestModel.name
$MODEL_VERSION = $latestModel.version

Write-Host "Selected model: $MODEL_NAME"
Write-Host "Selected version: $MODEL_VERSION"
Write-Host ""

if ([string]::IsNullOrEmpty($MODEL_NAME) -or [string]::IsNullOrEmpty($MODEL_VERSION)) {
    Write-Host "ERROR: Could not extract model name or version" -ForegroundColor Red
    exit 1
}

Write-Host "Step 4: Verifying model exists" -ForegroundColor Yellow
az ml model show `
    --name $MODEL_NAME `
    --version $MODEL_VERSION `
    --resource-group $ResourceGroup `
    --workspace-name $WorkspaceName `
    --subscription $SubscriptionId `
    --query '{name:name, version:version, type:type, path:path, createdTime:creation_context.created_at}' `
    -o table

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS: Model discovery and verification complete!" -ForegroundColor Green
    Write-Host "Model: $MODEL_NAME version $MODEL_VERSION is ready for deployment"
}
else {
    Write-Host ""
    Write-Host "❌ FAILED: Model verification failed" -ForegroundColor Red
}
