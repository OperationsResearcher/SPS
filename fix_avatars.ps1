
$path = "c:\SPY_Cursor\SP_Code\templates\admin_panel.html"
$content = Get-Content $path -Encoding UTF8
# Remove lines 774 to 1153 (1-based indices 774..1153)
# 0-based: 773..1152
# Keep 0..772 and 1153..end
$newContent = $content[0..772] + $content[1153..($content.Count-1)]
$newContent | Set-Content $path -Encoding UTF8
Write-Host "Done"
