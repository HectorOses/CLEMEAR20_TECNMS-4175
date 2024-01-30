# -*- mode: python; python-indent: 4 -*-
import ncs
import math
# from .resource_manager import id_allocator
# from resource_manager import id_allocator should work, but adding below to validate testing.
from home.nsoadmin.nso.ncs_run_CLtest.packages.resource_manager.python.resource_manager import id_allocator


class IdAllocationNanoService(ncs.application.NanoService):

    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.debug("NanoService create ", state)

        service_path = f"/l3mplsvpn[name='{service.name}']"
        # Reference function id_request(service, svc_xpath, username,
        #        pool_name, allocation_name, sync, requested_id=-1):
        id_allocator.id_request(service, service_path, tctx.username, 'vpn-id', service.name, False)

class L3MPLSNanoService(ncs.application.NanoService):

    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.debug("NanoService create ", state)
        
        vpn_id = id_allocator.id_read(tctx.username, root, 'vpn-id', service.name)
        self.log.info(f'Vpn ID read: {vpn_id}')        

        for link in service.link:

            vpn_link = {'pe-ip': link.pe_ip, 'ce-ip': link.ce_ip, 'rip-net': link.rip_net}

            # Calculate IP address from unique link ID: 172.x.y.z
            pe_ip_o2 = 16 + math.ceil(link.link_id / 4096)         # Second octet
            pe_ip_o3 = math.ceil((link.link_id % 4096) / 16)       # Third octet
            pe_ip_o4 = (link.link_id % 16) * 16 + 1                # Fourth octet
            ce_ip_o4 = pe_ip_o4 + 1                                # Fourth octet for CE side ( = PE + 1 )

            if not link.pe_ip:
                vpn_link['pe-ip'] = f'172.{pe_ip_o2}.{pe_ip_o3}.{pe_ip_o4}'
            if not link.ce_ip:
                vpn_link['ce-ip'] = f'172.{pe_ip_o2}.{pe_ip_o3}.{ce_ip_o4}'
            if not link.rip_net:
                vpn_link['rip-net'] = f'172.{pe_ip_o2}.0.0'

            tvars = ncs.template.Variables()
            template = ncs.template.Template(service)
            tvars.add('VPNID', vpn_id)
            tvars.add('DEVICE', link.device)
            tvars.add('PEIP', vpn_link['pe-ip'])
            tvars.add('CEIP', vpn_link['ce-ip'])
            tvars.add('ROUTING-PROTOCOL', link.routing_protocol)

            if link.routing_protocol == 'rip':
                tvars.add('RIP-NET', vpn_link['rip-net'])
            else:
                tvars.add('RIP-NET', '')

            tvars.add('INTERFACE', link.interface)
            self.log.info(f'Service create(applying template for device {link.device})')
            template.apply('l3mplsvpn-template', tvars)

        return proplist

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class L3MplsVpn(ncs.application.Application):
    def setup(self):
        self.log.info('L3MplsVpn RUNNING')
        self.register_nano_service('l3mplsvpn-servicepoint', 'l3mplsvpn:l3mplsvpn', 'l3mplsvpn:id-allocated', IdAllocationNanoService)
        self.register_nano_service('l3mplsvpn-servicepoint', 'l3mplsvpn:l3mplsvpn', 'l3mplsvpn:l3mplsvpn-configured', L3MPLSNanoService)


    def teardown(self):
        self.log.info('L3MplsVpn FINISHED')


