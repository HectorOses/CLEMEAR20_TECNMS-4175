# -*- mode: python; python-indent: 4 -*-
import ncs
import math
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vpn_id = service.vpn_id

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

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class L3MplsVpn(ncs.application.Application):
    def setup(self):
        self.log.info('L3MplsVpn RUNNING')
        self.register_service('l3mplsvpn-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('L3MplsVpn FINISHED')


