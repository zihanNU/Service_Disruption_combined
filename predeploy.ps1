###########################################################################################################################
#Copy and install Miniconda
###########################################################################################################################
#$file = "\\gxstorage\GXData\All Departmental Data\Information Technology\Jamie\Miniconda3-latest-Windows-x86_64.exe"
$file = "\\gxstorage\GXData\Test Files\Miniconda3-latest-Windows-x86_64.exe"

Copy-Item -Credential -Path $file -Destination 'c:\temp\Miniconda3-latest-Windows-x86_64.exe'

Invoke-Command -ScriptBlock {
    Start-Process "c:\temp\Miniconda3-latest-Windows-x86_64.exe" -ArgumentList "/S", "/InstallationType=AllUsers", "/RegisterPython=1", "/D=C:\Miniconda" -Wait
}