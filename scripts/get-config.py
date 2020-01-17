import ncs

# This first lines open a read transaction to NSO CDb
with ncs.maapi.Maapi() as m: 
    with ncs.maapi.Session(m, 'admin', 'python'): 
        with m.start_read_trans() as t:
            root = ncs.maagic.get_root(t)
            # From this point "root" is the base of our CDB to navigate

            device_name = "PE_10"

            dev = root.devices.device[device_name]
            hostname = dev.config.cisco_ios_xr__hostname;
            print "{} hostname: {}".format(device_name, str(hostname)); 

            # The following returns parameters for all configured Loopback interfaces
            for Loopback in dev.config.cisco_ios_xr__interface.Loopback:
                print "Loopback" + str(Loopback.id) + " IP address: " + str(Loopback.ipv4.address.ip)
