VScode - Remote SSH - Setup
================================

Taken from:
https://code.visualstudio.com/docs/remote/ssh

Installing a supported SSH client
-----------------------------------------

Install Git for Windows and select the Use Git and optional Unix tools from the Command Prompt option or manually add C:\Program Files\Git\usr\bin into your PATH.
https://git-scm.com/download/win

Setup shared keys
------------------

Taken from: https://code.visualstudio.com/docs/remote/troubleshooting#_configuring-key-based-authentication

1. Generate a separate SSH key in a different file.  
    On Windows, run the following command in a local command prompt:
    ```
    ssh-keygen -t rsa -b 4096 -f %USERPROFILE%\.ssh\id_rsa-remote-ssh
    ```
2. In VS Code, run Remote-SSH: Open Configuration File... in the Command Palette (F1), select an SSH config file, and add (or modify) a host entry as follows:
    ```
    Host name-of-ssh-host-here
        User your-user-name-on-host
        HostName host-fqdn-or-ip-goes-here
        IdentityFile ~/.ssh/id_rsa-remote-ssh
    ```
3. Add the contents of the local id_rsa-remote-ssh.pub file generated in step 1 to the appropriate authorized_keys file(s) on the remote host.  
    On Windows, run the following commands in a local command prompt, replacing name-of-ssh-host-here with the host name in the SSH config file from step 2.
    ```
    SET REMOTEHOST=name-of-ssh-host-here
    SET PATHOFIDENTITYFILE=%USERPROFILE%\.ssh\id_rsa-remote-ssh.pub

    scp %PATHOFIDENTITYFILE% %REMOTEHOST%:~/tmp.pub
    ssh %REMOTEHOST% "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat ~/tmp.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && rm -f ~/tmp.pub"
    ```