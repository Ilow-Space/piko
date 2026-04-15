# 1. Define the filename (The file containing the response text)
$inputFile = "./input.txt"

Write-Host "--- Starting Project Unpack Process ---" -ForegroundColor Yellow

# 2. Check if the file exists
if (-not (Test-Path $inputFile)) {
    Write-Host "ERROR: Could not find the file '$inputFile' in $(Get-Location)" -ForegroundColor Red
    return
}

Write-Host "Reading $inputFile..." -ForegroundColor Cyan

$currentFile = $null
$contentBuffer = [System.Collections.Generic.List[string]]::new()
$isCapturing = $false

# 3. Process the file
$lines = [System.IO.File]::ReadLines((Resolve-Path $inputFile))

foreach ($line in $lines) {
    # Match the start pattern: --- START FILE path/to/file ---
    if ($line -match "^--- START FILE (.*) ---") {
        $currentFile = $Matches[1].Trim()
        $contentBuffer.Clear()
        $isCapturing = $true
        continue
    }

    # Match the end pattern: --- END FILE  ---
    if ($line -match "^--- END FILE  ---") {
        if ($null -ne $currentFile) {
            # Normalize path for the current OS
            $normalizedPath = $currentFile.Replace('\', [System.IO.Path]::DirectorySeparatorChar).Replace('/', [System.IO.Path]::DirectorySeparatorChar).Trim()
            $fullPath = Join-Path (Get-Location) $normalizedPath
            $dir = Split-Path $fullPath
            
            # Create directory if it doesn't exist
            if ($dir -and -not (Test-Path $dir)) { 
                New-Item -ItemType Directory -Path $dir -Force | Out-Null 
            }
            
            # Write the captured content to the file
            [System.IO.File]::WriteAllLines($fullPath, $contentBuffer)
            Write-Host "Saved: $normalizedPath" -ForegroundColor Green
        }
        $isCapturing = $false
        $currentFile = $null
        continue
    }

    # Add lines to buffer if we are between START and END tags
    if ($isCapturing) {
        $contentBuffer.Add($line)
    }
}

Write-Host "--- Finished! ---" -ForegroundColor Yellow
