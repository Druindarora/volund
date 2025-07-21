Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
}
public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}
"@

# Obtenir le handle de la console cmd.exe
Add-Type -AssemblyName System.Windows.Forms
$consoleTitle = [System.Console]::Title
$hwnd = (Get-Process | Where-Object { $_.MainWindowTitle -eq $consoleTitle }).MainWindowHandle

if ($hwnd -eq 0) {
    Write-Output "⚠️ Impossible de localiser la fenêtre de la console."
    return
}

[RECT]$rect = New-Object RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null

$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top

Write-Output "Position actuelle : X=$($rect.Left), Y=$($rect.Top), Largeur=$width, Hauteur=$height"
