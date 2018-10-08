$session = New-PSSession -ComputerName PRDGXWEBSRV01 #-Credential $cred
$file = "c:\installers\Miniconda3-latest-Windows-x86_64.exe"

#Copy installer executable
Copy-Item -Path $file -ToSession $session -Destination 'c:\temp\Miniconda3-latest-Windows-x86_64.exe'

#Install miniconda
Invoke-Command -Session $session -ScriptBlock {
    Start-Process "c:\temp\Miniconda3-latest-Windows-x86_64.exe" -ArgumentList "/S", "/InstallationType=AllUsers", "/RegisterPython=1", "/D=C:\Miniconda" -Wait
}

Remove-PSSession $session