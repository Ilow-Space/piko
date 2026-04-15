# Output filename
$outputFile = "project_context.txt"
$rootPath = Get-Location

if (Test-Path $outputFile) { Remove-Item $outputFile }

# Find all .py files recursively
# We use Where-Object to filter out specific directories like .venv, .git, and __pycache__
$files = Get-ChildItem -Path "$rootPath\*" -Recurse -Include *.py, *.js, *.json , *.html | 
         Where-Object { 
            $_.FullName -notmatch [regex]::Escape(".venv") -and 
            $_.FullName -notmatch [regex]::Escape("venv") -and 
            $_.FullName -notmatch [regex]::Escape("webenv") -and 
            $_.FullName -notmatch [regex]::Escape("pyenv_ninja") -and 
            $_.FullName -notmatch [regex]::Escape(".git") -and 
            $_.FullName -notmatch [regex]::Escape("__pycache__")
         }

Write-Host "Found $($files.Count) files. Merging..." -ForegroundColor Cyan

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($rootPath.Path.Length)
    
    $header = "`n`n" + ("=" * 50) + "`n" + 
              "FILE PATH: $relativePath" + "`n" + 
              ("=" * 50) + "`n"

    $header | Out-File -FilePath $outputFile -Append -Encoding UTF8
    Get-Content -Path $file.FullName -Raw | Out-File -FilePath $outputFile -Append -Encoding UTF8
}

Write-Host "Done! All code saved to: $outputFile" -ForegroundColor Green