###########################################################################################################################
#Download and install Miniconda
###########################################################################################################################

$url = "https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$output = "c:\temp\Miniconda3-latest-Windows-x86_64.exe"
$start_time = Get-Date

$wc = New-Object System.Net.WebClient
$wc.DownloadFile($url, $output)

Invoke-Command -ScriptBlock {
    Start-Process "c:\temp\Miniconda3-latest-Windows-x86_64.exe" -ArgumentList "/S", "/InstallationType=AllUsers", "/RegisterPython=1", "/D=C:\Miniconda" -Wait
}