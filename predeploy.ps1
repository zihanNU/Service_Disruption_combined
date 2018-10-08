###########################################################################################################################
#Download and install Miniconda
###########################################################################################################################
Write-Host "Predeploy.ps1 -> Checking for Miniconda"
If(Test-Path C:\Miniconda -PathType Container)
{
    Write-Host "Predeploy.ps1 -> Miniconda found"
}
else
{
    Write-Host "Predeploy.ps1 -> Miniconda missing .. downloading"

    $url = "https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $output = "c:\temp\Miniconda3-latest-Windows-x86_64.exe"
    $start_time = Get-Date

    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($url, $output)


    Write-Host "Predeploy.ps1 -> Installing miniconda"
    Invoke-Command -ScriptBlock {
        Start-Process "c:\temp\Miniconda3-latest-Windows-x86_64.exe" -ArgumentList "/S", "/InstallationType=AllUsers", "/RegisterPython=1", "/D=C:\Miniconda" -Wait
    }   
}
Write-Host "Predeploy.ps1 -> Miniconda check complete"

###########################################################################################################################
#IIS Enable CGI
###########################################################################################################################
Write-Host "Predeploy.ps1 -> Enabling CGI in IIS"
Invoke-Command -ScriptBlock {
    Enable-WindowsOptionalFeature -Online -FeatureName IIS-CGI
}
Write-Host "Predeploy.ps1 -> Enable CGI in IIS - Complete"







