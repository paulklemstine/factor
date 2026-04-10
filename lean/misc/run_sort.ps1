$base = "\\wsl.localhost\Ubuntu\home\raver1975\lean"
$source = Join-Path $base "lean4"

# Create target directories
foreach ($d in @("research", "sciam", "lean", "visual", "demo", "teams", "misc")) {
    $target = Join-Path $base $d
    if (-not (Test-Path $target)) {
        New-Item -ItemType Directory -Path $target -Force | Out-Null
        Write-Host "Created directory: $d"
    }
}

# Get all files recursively, excluding this script
$files = Get-ChildItem -Path $source -Recurse -File | Where-Object { $_.Name -ne "run_sort.ps1" -and $_.Name -ne "sort_files.ps1" -and $_.Name -ne "sort_files.sh" }

Write-Host "Found $($files.Count) files to sort"

foreach ($file in $files) {
    $name = $file.Name
    $ext = $file.Extension.ToLower()
    $relPath = $file.FullName.Substring($source.Length + 1)
    $relDir = if ($relPath -match '\\') { $relPath.Substring(0, $relPath.LastIndexOf('\')) } else { "" }
    
    $category = $null
    
    # 1. Scientific American articles
    if ($name -match "(?i)SciAm|sciam|scientific_american") {
        $category = "sciam"
    }
    # 2. Research papers
    elseif ($name -match "(?i)ResearchPaper|research_paper") {
        $category = "research"
    }
    elseif ($relDir -match "(?i)papers" -and $name -match "(?i)research") {
        $category = "research"
    }
    # 3. Team files (non-lean)
    elseif ($name -match "(?i)team" -and $ext -ne ".lean") {
        $category = "teams"
    }
    # 4. Demo files
    elseif ($name -match "(?i)demo" -or $relDir -match "(?i)(^|\\)demos(\\|$)") {
        $category = "demo"
    }
    # 5. Visual files
    elseif ($ext -in @(".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico")) {
        $category = "visual"
    }
    elseif ($relDir -match "(?i)(^|\\)visuals(\\|$)") {
        $category = "visual"
    }
    # 6. Lean files
    elseif ($ext -eq ".lean") {
        $category = "lean"
    }
    # 7. Everything else
    else {
        $category = "misc"
    }
    
    # Build target path
    $targetDir = Join-Path $base $category
    if ($relDir) {
        $targetSubDir = Join-Path $targetDir $relDir
    } else {
        $targetSubDir = $targetDir
    }
    
    if (-not (Test-Path $targetSubDir)) {
        New-Item -ItemType Directory -Path $targetSubDir -Force | Out-Null
    }
    
    $targetPath = Join-Path $targetSubDir $name
    
    try {
        Move-Item -Path $file.FullName -Destination $targetPath -Force -ErrorAction Stop
    } catch {
        Write-Host "ERROR: $relPath - $_"
    }
}

# Print summary
Write-Host ""
Write-Host "=== File Organization Complete ==="
foreach ($d in @("research", "sciam", "lean", "visual", "demo", "teams", "misc")) {
    $target = Join-Path $base $d
    $count = (Get-ChildItem -Path $target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "${d}: $count files"
}
