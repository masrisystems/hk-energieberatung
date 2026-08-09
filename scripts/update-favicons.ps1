# update-favicons.ps1
# Updates favicon tags in all HTML files across the project

$baseDir = "c:\Users\super\Desktop\Hk Energieberatung"

# The HTML files to update
$htmlFiles = Get-ChildItem -Path $baseDir -Filter "*.html" -Recurse | Where-Object { $_.Name -ne "old.html" }

# Old favicon block patterns to replace
$oldPatterns = @(
    # Pattern 1: comment + logo.jpeg for icon + logo.jpeg for apple-touch
    '(?s)  <!-- Favicons -->\r?\n  <link href="assets/img/logo\.jpeg" rel="icon">\r?\n  <link href="assets/img/logo\.jpeg" rel="apple-touch-icon">',
    # Pattern 2: logo.jpeg just as icon (no comment, no apple-touch)
    '(?s)  <link href="assets/img/logo\.jpeg" rel="icon">\r?\n  <link href="assets/img/logo\.jpeg" rel="apple-touch-icon">',
    # Pattern 3: favicon.png for icon + apple-touch-icon
    '(?s)  <link href="assets/img/favicon\.png" rel="icon">\r?\n  <link href="assets/img/apple-touch-icon\.png" rel="apple-touch-icon">',
    # Pattern 4: just favicon.png for icon
    '  <link href="assets/img/favicon\.png" rel="icon">'
)

$newFaviconBlock = '  <!-- Favicons -->
  <link rel="icon" type="image/x-icon" href="assets/img/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/img/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">'

$count = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    
    # Try replacing with comment pattern first
    if ($content -match '<!-- Favicons -->') {
        # Has comment
        $pattern = '(?s)([ \t]*)<!-- Favicons -->[ \t]*\r?\n[ \t]*<link[^>]+rel="icon"[^>]*>[ \t]*\r?\n[ \t]*<link[^>]+rel="apple-touch-icon"[^>]*>'
        $replacement = $newFaviconBlock
        $content = [regex]::Replace($content, $pattern, $replacement)
    } else {
        # No comment, just the icon links
        $pattern1 = '(?s)([ \t]*)<link[^>]+rel="icon"[^>]*>[ \t]*\r?\n[ \t]*<link[^>]+rel="apple-touch-icon"[^>]*>'
        if ($content -match $pattern1) {
            $content = [regex]::Replace($content, $pattern1, $newFaviconBlock)
        } elseif ($content -match '<link[^>]+rel="icon"[^>]*>') {
            # Only has icon, no apple-touch-icon
            $pattern2 = '([ \t]*)<link[^>]+rel="icon"[^>]*>'
            $content = [regex]::Replace($content, $pattern2, $newFaviconBlock)
        }
    }
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Output "Updated: $($file.Name)"
        $count++
    } else {
        Write-Output "Skipped (no match): $($file.Name)"
    }
}

Write-Output "`nDone! Updated $count files."
