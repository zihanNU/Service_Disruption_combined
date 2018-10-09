This folder contains powershell scripts designed to get a python/flask applciation
up and running on a server.

These scripts are designed to be run on a remote machine, specifying the target machine.

************************************************************
** THESE SCRIPTS ARE NOT CURRENTLY MAINTAINED (10/9/2018) **
************************************************************

The updated script to solve this problem is in the predeploy.ps1 script in the root folder of MatchingResearch001.
Using built in Octopus conventions for running predeploy.<ext> scripts, there is no need to detect the target server.
predeploy.ps1 has the 4 sections represented by these files

 01.Install.Miniconda.ToRemote.ps1 = #Download and install Miniconda
 02.IIS.EnableCGI.ToRemote.ps1 = #IIS Enable CGI
 03.Conda.Installs.ps1 = #Conda Installs
 04.RemainingSteps.ps1 = This is still TODO ... Unsure whether this should be in Octopus variables, or just keep it in PS
    scripts since the miniconda location is specified here anyway.


See Jamie for questions.