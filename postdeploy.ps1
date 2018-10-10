###########################################################################################################################
#Update Web.Config 
###########################################################################################################################
Write-Host "Postdeploy.ps1 -> Update web.config"
$success = 0
[xml]$configDoc  = Get-Content -Path "./web.config"
$handlersNode = $configDoc["configuration"].'system.webServer'.handlers

ForEach($n in $handlersNode.ChildNodes) {
    if($n.Attributes["name"].Value -eq "Python FastCGI")
    {
        $n.Attributes["scriptProcessor"].Value = "C:\Miniconda\python.exe|C:\Miniconda\lib\site-packages\wfastcgi.py"
        $configDoc.Save((Get-Item -Path ".\").FullName + "\web.config")
        $success = 1
    }
}
Write-Host "Postdeploy.ps1 -> Update web.config complete: " + $success
