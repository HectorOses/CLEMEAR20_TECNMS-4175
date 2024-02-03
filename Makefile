export NSO_VERSION=6.1.5

# Restore packages for exercise

load-initial-packages:
	rm -r /var/opt/ncs/packages/*
# link neds, copy loopback-basic and l3mplsvpn
# then use chown to make nsoadmin:ncsadmin the owner


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
	