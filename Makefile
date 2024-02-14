export NSO_VERSION=6.1.5

# Restore packages for exercise

load-initial-packages:
	echo -e "config\nno l3mplsvpn\ncommit" | ncs_cli -C
	rm -r /var/opt/ncs/packages/*
	ln -s /opt/ncs/current/packages/neds/cisco-ios-cli-6.100 /var/opt/ncs/packages/
	ln -s /opt/ncs/current/packages/neds/cisco-iosxr-cli-7.53 /var/opt/ncs/packages/
	ln -s /opt/ncs/current/packages/neds/juniper-junos-nc-4.14 /var/opt/ncs/packages/
	cp -r /home/cisco/CLEMEAR20_TECNMS-4175/TECOPS2201_initial/l3mplsvpn /var/opt/ncs/packages/
	cp -r /home/cisco/CLEMEAR20_TECNMS-4175/packages/loopbackbasic /var/opt/ncs/packages/
	echo "packages reload force" | ncs_cli -C
	echo "show packages package oper-status | tab" | ncs_cli -C

load-nano-l3mplsvpn-manual:
	echo -e "config\nno l3mplsvpn\ncommit" | ncs_cli -C
	rm -r /var/opt/ncs/packages/*
	ln -s /opt/ncs/current/packages/neds/cisco-ios-cli-6.100 /var/opt/ncs/packages/
	ln -s /opt/ncs/current/packages/neds/cisco-iosxr-cli-7.53 /var/opt/ncs/packages/
	ln -s /opt/ncs/current/packages/neds/juniper-junos-nc-4.14 /var/opt/ncs/packages/
	cp -r /home/cisco/CLEMEAR20_TECNMS-4175/TECOPS2201_solutions/nano-services-manual-solution/l3mplsvpn /var/opt/ncs/packages/
	echo "packages reload force" | ncs_cli -C
	echo "show packages package oper-status | tab" | ncs_cli -C

# Netsim 

create-netsim:
	ncs-netsim create-device packages/cisco-ios-cli-6.100 PE_00
	ncs-netsim add-device packages/cisco-ios-cli-6.100 PE_01
	ncs-netsim add-device packages/cisco-iosxr-cli-7.53 PE_10
	ncs-netsim add-device packages/cisco-iosxr-cli-7.53 PE_11

load-netsim-devices:
	ncs-netsim ncs-xml-init > devices.xml
	ncs_load -l -m devices.xml

delete-netsim: 
	ncs-netsim stop
	ncs-netsim delete-network

start-netsim:
	ncs-netsim start

rebuild-netsim: delete-netsim create-netsim load-netsim-devices start-netsim
	