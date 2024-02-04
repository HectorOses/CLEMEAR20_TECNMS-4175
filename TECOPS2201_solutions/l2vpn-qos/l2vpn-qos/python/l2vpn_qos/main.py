import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        # Get the service instance inputs
        service_id = service.service_id
        pw_id = service.pseudowire_id
        vlan_id = service.vlan_id
        pe_infos = [{"pe_device":device.pe_device,"pe_ce_interface_id":device.pe_ce_interface_id} for device in service.pe_devices]
        average_bit_rate = service.average_bit_rate
        ce_infos = [{"ce_device":device.ce_device,"lan_ge_interface_id":device.lan_ge_interface_id} for device in service.ce_devices]

        # We will auto-generate the policy-name that by concatinating the service_id to the average_bit_rate        
        policy_name = service_id + "_" + str(average_bit_rate)

        # From NSO CDB we will get the loopbcack IP of PE device
        for pe in pe_infos:
            pe_device = root.devices.device[pe["pe_device"]]
            # We need to check the device type to know the correct path to get loopbcack ip address
            if pe_device.platform.name in ["ios", "ios-xe"]:
                loopback_ip = pe_device.config.interface.Loopback['0'].ip.address.primary.address
            elif pe_device.platform.name == "ios-xr":
                loopback_ip = pe_device.config.interface.Loopback['0'].ipv4.address.ip
            elif pe_device.platform.name == "junos":
                # For Junos the the address is of type list, so we will convert the the YANG List to Python List using ncs.maagic.as_pyval and then read the 
                # first item in that list 
                loopback_ip = ncs.maagic.as_pyval(pe_device.config.configuration.interfaces.interface['lo0'].unit['0'].family.inet.address)[0]["name"]
                # The ip addresses in JunOS are written in CIDR notation X.X.X.X/Y so we need to get only the IP address
                loopback_ip = loopback_ip.split("/")[0]
            pe["loopback_ip"] = loopback_ip

        # For each PE device we need to have the neighbor PE loopback IP
        for pe_info in pe_infos:
            pe_info["neighbor_pe_loopback"] = next(item["loopback_ip"] for item in pe_infos if item != pe_info)

        # Add the needed variables and apply them to the respective template
        l2vpn_vars = ncs.template.Variables()
        l2vpn_template = ncs.template.Template(service)
        l2vpn_vars.add('name', service_id)
        l2vpn_vars.add('pseudowire_id', pw_id)
        l2vpn_vars.add('vlan_id', vlan_id)
        for pe in pe_infos:
            l2vpn_vars.add('pe_device', pe['pe_device'])
            l2vpn_vars.add('neighbor_pe_loopback', pe['neighbor_pe_loopback'])
            l2vpn_vars.add('pe_ce_interface_id', pe['pe_ce_interface_id'])
            l2vpn_template.apply('l2vpn-stacked-template', l2vpn_vars)

        qos_vars = ncs.template.Variables()
        qos_template = ncs.template.Template(service)
        qos_vars.add('service_id', service_id)
        qos_vars.add('average_bit_rate', average_bit_rate)
        qos_vars.add('policy_name', policy_name)
        for ce in ce_infos:
            qos_vars.add('ce_device', ce["ce_device"])
            qos_vars.add('lan_ge_interface', ce["lan_ge_interface_id"])
            qos_template.apply('qos-stacked-template', qos_vars)


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l2vpn-qos-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
