Add-Type -AssemblyName System.Drawing

$srcPath = "c:\Users\super\Desktop\Hk Energieberatung\assets\img\logo.jpeg"
$src = [System.Drawing.Bitmap]::FromFile($srcPath)

function GenerateIcon([int]$targetSize, [string]$outPath, [double]$fillPercent = 0.82) {
    $bmp = New-Object System.Drawing.Bitmap($targetSize, $targetSize, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    
    # White background for optimal legibility across both dark and light mode
    $g.Clear([System.Drawing.Color]::White)

    # Source mark dimensions: width 361, height 224
    $srcW = 361.0
    $srcH = 224.0
    
    # Calculate target dimensions maintaining aspect ratio
    $markW = $targetSize * $fillPercent
    $markH = $markW * ($srcH / $srcW)
    
    $destX = ($targetSize - $markW) / 2.0
    $destY = ($targetSize - $markH) / 2.0
    
    $srcRect = New-Object System.Drawing.Rectangle(238, 46, 361, 224)
    $destRect = New-Object System.Drawing.RectangleF($destX, $destY, $markW, $markH)
    
    $g.DrawImage($src, $destRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
    
    $g.Dispose()
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Output "Generated: $outPath ($targetSize x $targetSize)"
}

$imgDir = "c:\Users\super\Desktop\Hk Energieberatung\assets\img"
$rootDir = "c:\Users\super\Desktop\Hk Energieberatung"

# Generate various sizes
GenerateIcon 16 "$imgDir\favicon-16x16.png" 0.88
GenerateIcon 32 "$imgDir\favicon-32x32.png" 0.85
GenerateIcon 48 "$imgDir\favicon-48x48.png" 0.84
GenerateIcon 96 "$imgDir\favicon-96x96.png" 0.82
GenerateIcon 180 "$imgDir\apple-touch-icon.png" 0.82
GenerateIcon 192 "$imgDir\favicon-192x192.png" 0.80
GenerateIcon 512 "$imgDir\favicon-512x512.png" 0.80

# Also copy primary favicon.png to assets/img and root
GenerateIcon 48 "$imgDir\favicon.png" 0.84
GenerateIcon 48 "$rootDir\favicon.png" 0.84
GenerateIcon 180 "$rootDir\apple-touch-icon.png" 0.82

$src.Dispose()
