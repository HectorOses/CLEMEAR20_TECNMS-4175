Introduction to the Lab
================

### Git Pull in Windows, NSO 1 and NSO 2

#### Windows Git Pull

Open Git Bash application from the desktop and perform below commands:

```
cd /c/dcloud/CLEMEA24_AMS_TECOPS-2201/CLEMEA23_TECNMS-4175
git pull
```

#### NSO 1 and NSO 2 Git Pull

Open Putty session from the Desktop "NSO 1 Host" and execute:

> **NOTE:** password for `nsoadmin` is `nsoadmin`

Only in NSO2. Open Putty session "NSO 2 Host"

```
sudo mkhomedir_helper nsoadmin
sudo usermod -aG cisco nsoadmin
su nsoadmin
echo 'source /opt/ncs/current/ncsrc' >> ~/.bashrc
source /opt/ncs/current/ncsrc
```

In both NSO1 and NSO2. Open Putty session "NSO 2 Host"

```
cd CLEMEAR20_TECNMS-4175/
sudo git config --global --add safe.directory /home/cisco/CLEMEAR20_TECNMS-4175
sudo git pull
sudo chown -R nsoadmin:ncsadmin /home/cisco/CLEMEAR20_TECNMS-4175
su nsoadmin
git pull
rm /var/opt/ncs/Makefile
cp /home/cisco/CLEMEAR20_TECNMS-4175/Makefile /var/opt/ncs/
cp -r /home/cisco/CLEMEAR20_TECNMS-4175/config_examples /var/opt/ncs/
cp -r /home/cisco/CLEMEAR20_TECNMS-4175/TECOPS-2201* /var/opt/ncs
```

Close the Putty session and open now "NSO 2 Host" and execute the same commands
