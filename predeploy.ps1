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


###########################################################################################################################
#Conda Installs
###########################################################################################################################

Write-Host "Predeploy.ps1 -> Conda Install wfastcgi"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "clinicalgraphics/label/archived", "wfastcgi" -Wait
}

Write-Host "Predeploy.ps1 -> wfastcgi-enable"
Invoke-Command -ScriptBlock {
    Invoke-Expression "c:\miniconda\scripts\wfastcgi-enable.exe" -ErrorAction SilentlyContinue
}


Write-Host "Predeploy.ps1 -> Conda Install flask"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "flask" -Wait
}

Write-Host "Predeploy.ps1 -> Conda Install pyodbc"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "pyodbc" -Wait
}

Write-Host "Predeploy.ps1 -> Conda Install pandas"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "pandas" -Wait
}

Write-Host "Predeploy.ps1 -> Conda Install scipy"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "anaconda", "scipy" -Wait
}

Write-Host "Predeploy.ps1 -> Conda Install geopy"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "conda-forge", "geopy" -Wait
}

Write-Host "Predeploy.ps1 -> Conda Install pytictoc"
Invoke-Command -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "ecf", "pytictoc" -Wait
}




