$session = New-PSSession -ComputerName PRDGXWEBSRV01 #-Credential $cred

Invoke-Command -Session $session -ScriptBlock {
    Enable-WindowsOptionalFeature -Online -FeatureName IIS-CGI
}

Remove-PSSession $session