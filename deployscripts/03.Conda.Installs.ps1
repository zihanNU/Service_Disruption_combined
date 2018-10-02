$session = New-PSSession -ComputerName PRDGXWEBSRV01 #-Credential $cred

#Invoke conda install wfastcgi
#Unsure if we can both install miniconda and wfastcgi in the same script....or if this will need to be two seperate calls.
Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "clinicalgraphics/label/archived", "wfastcgi" -Wait
}
Invoke-Command -Session $session -ScriptBlock {
    Invoke-Expression "c:\miniconda\scripts\wfastcgi-enable.exe"
}

#Invoke conda install application specific libraries
Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "flask" -Wait
}

Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "pyodbc" -Wait
}

Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "pandas" -Wait
}

Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "anaconda", "scipi" -Wait
}

#Pretty sure this is a type-o and can be removed (10/2/2018)
#Invoke-Command -Session $session -ScriptBlock {
#    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "geopi" -Wait
#}

Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "conda-forge", "geopy" -Wait
}

Invoke-Command -Session $session -ScriptBlock {
    Start-Process "C:\Miniconda\Scripts\conda.exe" -ArgumentList "install", "-y", "-c", "ecf", "pytictoc" -Wait
}


Remove-PSSession $session

  




