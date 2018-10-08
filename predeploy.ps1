###########################################################################################################################
#Download and install Miniconda
###########################################################################################################################
Write-Host "predeploy.ps1 process - downloading miniconda"
$url = "https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$output = "c:\temp\Miniconda3-latest-Windows-x86_64.exe"
$start_time = Get-Date

$wc = New-Object System.Net.WebClient
$wc.DownloadFile($url, $output)


Write-Host "predeploy.ps1 process - installing miniconda"
Invoke-Command -ScriptBlock {
    Start-Process "c:\temp\Miniconda3-latest-Windows-x86_64.exe" -ArgumentList "/S", "/InstallationType=AllUsers", "/RegisterPython=1", "/D=C:\Miniconda" -Wait
}