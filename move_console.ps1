Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@
Add-Type -AssemblyName System.Windows.Forms
$hwnd = (Get-Process | Where-Object { $_.MainWindowTitle -eq [Console]::Title }).MainWindowHandle
[Win32]::MoveWindow($hwnd, -967, 0, 974, 1039, $true)
