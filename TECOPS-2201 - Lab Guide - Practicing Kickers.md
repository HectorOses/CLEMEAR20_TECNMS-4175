TECOPS-2201 - Lab Guide - Practicing Kickers
==================

To make sure we start the exercise with the required packages run the following under `/var/opt/ncs` directory

```bash
make load-initial-packages
```

The command might take a while to complete as executes a packages reload inside NSO. When it finishes it will show the output of `show packages package oper-status` showing if the packages were properly loaded

```bash
echo "show packages package oper-status | tab" | ncs_cli -C
                                                                                                         PACKAGE                          
                           PROGRAM                                                                       META     FILE                    
                           CODE     JAVA           PYTHON         BAD NCS  PACKAGE  PACKAGE  CIRCULAR    DATA     LOAD   ERROR            
NAME                   UP  ERROR    UNINITIALIZED  UNINITIALIZED  VERSION  NAME     VERSION  DEPENDENCY  ERROR    ERROR  INFO   WARNINGS  
------------------------------------------------------------------------------------------------------------------------------------------
cisco-ios-cli-6.100    X   -        -              -              -        -        -        -           -        -      -      -         
cisco-iosxr-cli-7.53   X   -        -              -              -        -        -        -           -        -      -      -         
juniper-junos-nc-4.14  X   -        -              -              -        -        -        -           -        -      -      -         
l3mplsvpn              X   -        -              -              -        -        -        -           -        -      -      -         
loopbackbasic          X   -        -              -              -        -        -        -           -        -      -      -         
```

Harsh Service Redeploy on Device Offline Changes
---------------------

We don't expect anybody to touch the configuration of our service offline, on the devices, but... we know someone might "forget" about it and mess around with the validated configuration. So we decide that if we detect any changes in the device we'll re-deploy our service, just in case.

We are using already NSO scheduler to do a sync-from of the devices every night, but we don't want to write an action that does check-sync and if any changes do a sync-from and re-deploy. So we'll just monitor on changes on the devices and kick a re-deploy of the services.

First we'll configure a simple l3mpls service. As user `nsoadmin` from `var/opt/ncs` directory go into NSO CLI `ncs_cli -C`

```bash
nsoadmin@ncs# config
Entering configuration mode terminal
nsoadmin@ncs(config)# load merge load_payloads/l3mplsvpn_basic_service.cfg 
Loading.
136 bytes parsed in 0.03 sec (3.32 KiB/sec)
nsoadmin@ncs(config)# show config
l3mplsvpn vpn3
 vpn-id   128
 customer ACME
 link 1
  device    PE_00
  interface 0/0
 !
 link 2
  device    PE_10
  interface 0/1
 !
!
nsoadmin@ncs(config)# 
```

Let's check what we are going to configure on which devices with `commit dry-run` and then `commit` the configuration. Focus in the interface that is created on each PE_00 and PE_10, which we will later modify.

```bash
nsoadmin@ncs(config)# commit dry-run 
cli {
    local-node {
        data  devices {
                  device PE_00 {
                      config {
                          vrf {
             +                definition vpn128 {
             +                    rd 1:128;
             +                    route-target {
             +                        export 1:128;
             +                        import 1:128;
             +                    }
             +                    address-family {
             +                        ipv4 {
             +                        }
             +                    }
             +                }
                          }
                          interface {
                              GigabitEthernet 0/0 {
                                  vrf {
             +                        forwarding vpn128;
                                  }
                                  ip {
                                      no-address {
             -                            address false;
                                      }
                                      address {
                                          primary {
             +                                address 172.17.1.17;
             +                                mask 255.255.255.252;
                                          }
                                      }
                                  }
                              }
                          }
                          router {
             +                bgp 1 {
             +                    address-family {
             +                        with-vrf {
             +                            ipv4 unicast {
             +                                vrf vpn128 {
             +                                    redistribute {
             +                                        connected {
             +                                        }
             +                                        static {
             +                                        }
             +                                    }
             +                                    neighbor 172.17.1.18 {
             +                                        remote-as 65001;
             +                                    }
             +                                }
             +                            }
             +                        }
             +                    }
             +                }
                          }
                      }
                  }
                  device PE_10 {
                      config {
                          vrf {
             +                vrf-list vpn128 {
             +                    address-family {
             +                        ipv4 {
             +                            unicast {
             +                                import {
             +                                    route-target {
             +                                        address-list 1:128;
             +                                    }
             +                                }
             +                                export {
             +                                    route-target {
             +                                        address-list 1:128;
             +                                    }
             +                                }
             +                            }
             +                        }
             +                    }
             +                }
                          }
                          interface {
             +                GigabitEthernet 0/1 {
             +                    vrf vpn128;
             +                    ipv4 {
             +                        address {
             +                            ip 172.17.1.33;
             +                            mask 255.255.255.252;
             +                        }
             +                    }
             +                }
                          }
             +            route-policy pass {
             +                value pass;
             +            }
                          router {
                              bgp {
             +                    bgp-no-instance 1 {
             +                        vrf vpn128 {
             +                            rd 1:128;
             +                            address-family {
             +                                ipv4 {
             +                                    unicast {
             +                                        redistribute {
             +                                            connected {
             +                                            }
             +                                            static {
             +                                            }
             +                                        }
             +                                    }
             +                                }
             +                            }
             +                            neighbor 172.17.1.34 {
             +                                remote-as 65001;
             +                                address-family {
             +                                    ipv4 {
             +                                        unicast {
             +                                            route-policy in {
             +                                                name pass;
             +                                            }
             +                                            route-policy out {
             +                                                name pass;
             +                                            }
             +                                            as-override {
             +                                            }
             +                                            default-originate {
             +                                            }
             +                                        }
             +                                    }
             +                                }
             +                            }
             +                        }
             +                    }
                              }
                          }
                      }
                  }
              }
             +l3mplsvpn vpn3 {
             +    vpn-id 128;
             +    customer ACME;
             +    link 1 {
             +        device PE_00;
             +        interface 0/0;
             +    }
             +    link 2 {
             +        device PE_10;
             +        interface 0/1;
             +    }
             +}
    }
}
nsoadmin@ncs(config)# commit
Commit complete.
nsoadmin@ncs(config)# end
nsoadmin@ncs# 
```

> **OPTIONAL:** If you want to look more in detail how kickers act you can leave open in another terminal in VS Code, or in a separate Putty session the devel.log file
> 
> ```bash
> nsoadmin@cisco-virtual-machine:/var/log/ncs$ tail -f devel.log
> <DEBUG> 1-Feb-2024::22:08:46.072 cisco-virtual-machine ncs[189782][<0.12665.5>]: ncs progress usid=171 tid=5058 datastore=operational context=system trace-id=6cdd0d4c-bbbf-480e-bb35-88ea363bff60 check data kickers
> <DEBUG> 1-Feb-2024::22:08:46.072 cisco-virtual-machine ncs[189782][<0.12665.5>]: ncs progress usid=171 tid=5058 datastore=operational context=system trace-id=6cdd0d4c-bbbf-480e-bb35-88ea363bff60 check data kickers: ok (0.000 s)
> ...
> ```
> 
> As well it might be interesting to leave open the l3mplsvpn service python vm file `ncs-python-vm-l3mplsvpn.log`.

The ncs.conf file has already been updated to show kickers, but before we can see them or configure them on the cli we need to `unhide debug`.

```bash
nsoadmin@ncs# unhide debug
nsoadmin@ncs# 
```

### Task 1

Let's start simple, where for any changes on any devices we will re-deploy our L3VPN service.

Create a kicker that monitors any changes on all devices and triggers the redeploy of our l3mplsvpn vpn3 service. Remember that you can use the `| display xpath` or including prefixes `| display xpath | display prefixes` with any `show running-config` command to find the xpath you want to monitor.

For example

```bash
nsoadmin@ncs# show running-config devices device PE_00 address | display xpath
/devices/device[name='PE_00']/address 127.0.0.1
nsoadmin@ncs# show running-config devices device PE_00 address | display xpath | display prefixes 
/ncs:devices/ncs:device[ncs:name='PE_00']/ncs:address 127.0.0.1
nsoadmin@ncs# 
```

```bash
nsoadmin@ncs(config)# kickers data-kicker redeploy-l3mplsvpn-on-device-change
Value for 'monitor' (<string>): /ncs:devices/ncs:device
Value for 'kick-node' : /l3mplsvpn:l3mplsvpn
Value for 'action-name' (<string, min: 1 chars>): re-deploy
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# show config
kickers data-kicker redeploy-l3mplsvpn-on-device-change
 monitor     /ncs:devices/ncs:device
 kick-node   /l3mplsvpn:l3mplsvpn
 action-name re-deploy
!
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# commit
Commit complete.
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# 
```

Remember that a kicker becomes active as soon as you commit its confiuration.

If you have devel.log open you can find the following lines indicating the kicker has been applied

```log
<DEBUG> 30-Jan-2024::12:45:35.874 cisco-virtual-machine ncs[189782][<0.2079.0>]: ncs progress usid=49 tid=4129 datastore=running context=cli trace-id=2801a9ea-dc67-4db5-a58e-f7aab5507721 subsystem=kicker internal at /kicker:kickers changed; invoking kicker_server:kicker_data_changed/4
<INFO> 30-Jan-2024::12:45:35.874 cisco-virtual-machine ncs[189782][<0.2079.0>]: ncs progress usid=49 tid=4129 datastore=running context=cli trace-id=2801a9ea-dc67-4db5-a58e-f7aab5507721 check data kickers: ok (0.000 s)
...
<INFO> 30-Jan-2024::12:45:35.879 cisco-virtual-machine ncs[189782][<0.2079.0>]: ncs progress usid=49 tid=4129 datastore=running context=cli trace-id=2801a9ea-dc67-4db5-a58e-f7aab5507721 invoking data kickers
<INFO> 30-Jan-2024::12:45:35.879 cisco-virtual-machine ncs[189782][<0.2079.0>]: ncs progress usid=49 tid=4129 datastore=running context=cli trace-id=2801a9ea-dc67-4db5-a58e-f7aab5507721 invoking data kickers: ok (0.000 s)
```

We do sync-from but nothing has changed on the devices

```
nsoadmin@ncs# devices device PE_00 sync-from 
result true
nsoadmin@ncs# 
```

If you have the devel.log open you can see there that actually no kicker was triggered

Let's now make an offline change on PE_00, but without touching the L3VPN service. The re-deploy will happen, but there won't be any changes to push to the device

> **NOTE:** We are using simulated NSO NETSIM devices to use `ncs-netsim cli-c <device-name>` to connect to them

```
nsoadmin@cisco-virtual-machine:~/nso/ncs-run_CLtest$ ncs-netsim cli-c PE_00

User admin last logged in 2024-01-30T11:47:40.282086+00:00, to cisco-virtual-machine, from 127.0.0.1 using cli-ssh
admin connected from 10.227.64.241 using ssh on cisco-virtual-machine
PE_00# config
Entering configuration mode terminal
PE_00(config)# interface GigabitEthernet 0/2
PE_00(config-if)# description I was here
PE_00(config-if)# commit
Commit complete.
PE_00(config-if)# 
```

To avoid having to schedule the sync-from and wait for it we will trigger it manually

```bash
nsoadmin@ncs# devices device PE_00 sync-from 
result true
nsoadmin@ncs# 
```

devel.log shows the kicker was triggered

```
<INFO> 30-Jan-2024::12:51:17.154 cisco-virtual-machine ncs[189782][<0.2877.0>]: ncs progress usid=49 tid=4165 datastore=running context=cli trace-id=bbc15b25-635f-4af0-8641-535338af918e check data kickers
<DEBUG> 30-Jan-2024::12:51:17.155 cisco-virtual-machine ncs[189782][<0.2877.0>]: ncs progress usid=49 tid=4165 datastore=running context=cli trace-id=bbc15b25-635f-4af0-8641-535338af918e subsystem=kicker redeploy-l3mplsvpn-on-device-change at /ncs:devices/ncs:device[ncs:name='PE_00'] changed; invoking 're-deploy'
...

```

And if you have the service log open (ncs-python-vm-l3mplsvpn.log) you can see the create was applied again

```log
<INFO> 30-Jan-2024::12:51:17.198 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-3-th-4188: - Service create(service=/l3mplsvpn:l3mplsvpn{vpn3})
<INFO> 30-Jan-2024::12:51:17.203 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-3-th-4188: - Service create(applying template for device PE_00)
<INFO> 30-Jan-2024::12:51:17.221 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-3-th-4188: - Service create(applying template for device PE_10)
```

Now, the device configuration has not changed as interface GigabitEthernet 0/2 is not owned by our service

```bash
nsoadmin@ncs# show running-config devices device PE_00 config interface GigabitEthernet 0/2 description 
devices device PE_00
 config
  interface GigabitEthernet0/2
   description I was here...
  exit
 !
!
nsoadmin@ncs#
```

Now we will modify the configured IP in GigabitEthernet 0/0, which is owned by our L3VPN service.

Current configuration is the following

```
nsoadmin@ncs# show running-config devices device PE_00 config interface GigabitEthernet 0/0 
devices device PE_00
 config
  interface GigabitEthernet0/0
   no switchport
   vrf forwarding vpn128
   ip address 172.17.1.17 255.255.255.252
   no shutdown
  exit
 !
!
nsoadmin@ncs# 
```

As a reminder we can check that the configuration is owned by our service and only by our service (refcount is 1).

```bash
nsoadmin@ncs# show running-config devices device PE_00 config interface GigabitEthernet 0/0 | display service-meta-data              
devices device PE_00
 config
  ! Refcount: 1
  ! Backpointer: [ /l3mplsvpn:l3mplsvpn[l3mplsvpn:name='vpn3'] ]
  interface GigabitEthernet0/0
   no switchport
   ! Refcount: 1
   vrf forwarding vpn128
   ! Refcount: 1
   ip address 172.17.1.17 255.255.255.252
   no shutdown
  exit
 !
!
nsoadmin@ncs#
```

Directly on the device

```bash
nsoadmin@cisco-virtual-machine:/var/opt/ncs$ ncs-netsim cli-c PE_00

User admin last logged in 2024-02-01T21:43:28.406265+00:00, to cisco-virtual-machine, from 127.0.0.1 using cli-ssh
admin connected from 10.227.64.241 using ssh on cisco-virtual-machine
PE_00# config
Entering configuration mode terminal
PE_00(config)# interface GigabitEthernet 0/0 ip address 172.27.1.17 255.255.255.255
PE_00(config-if)# commit
Commit complete.
PE_00(config-if)# 
```

Now we will do sync-from again, but this time the service re-deploy will find is not in sync as the IP has changed and will push back the original IP configuration.

```
nsoadmin@ncs# devices device PE_00 sync-from                                                           
result true
nsoadmin@ncs# show running-config devices device PE_00 config interface GigabitEthernet 0/0
devices device PE_00
 config
  interface GigabitEthernet0/0
   no switchport
   vrf forwarding vpn128
   ip address 172.17.1.17 255.255.255.252
   no shutdown
  exit
 !
!
nsoadmin@ncs# 
```

In devel.log we can see again the kicker was triggered

```log
<INFO> 30-Jan-2024::13:00:21.779 cisco-virtual-machine ncs[189782][<0.3572.0>]: ncs progress usid=49 tid=4208 datastore=running context=cli trace-id=a90a3477-065e-4736-bd77-e3fbd7b5c753 check data kickers
<DEBUG> 30-Jan-2024::13:00:21.780 cisco-virtual-machine ncs[189782][<0.3572.0>]: ncs progress usid=49 tid=4208 datastore=running context=cli trace-id=a90a3477-065e-4736-bd77-e3fbd7b5c753 subsystem=kicker redeploy-l3mplsvpn-on-device-change at /ncs:devices/ncs:device[ncs:name='PE_00'] changed; invoking 're-deploy'
...

```

And in the l3mplsvpn python vm log we see the create called again

```log
<INFO> 30-Jan-2024::13:00:21.822 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4230: - Service create(service=/l3mplsvpn:l3mplsvpn{vpn3})
<INFO> 30-Jan-2024::13:00:21.827 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4230: - Service create(applying template for device PE_00)
<INFO> 30-Jan-2024::13:00:21.849 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4230: - Service create(applying template for device PE_10)
<INFO> 30-Jan-2024::13:00:25.537 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4270: - Service create(service=/l3mplsvpn:l3mplsvpn{vpn3})
<INFO> 30-Jan-2024::13:00:25.543 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4270: - Service create(applying template for device PE_00)
<INFO> 30-Jan-2024::13:00:25.565 l3mplsvpn ncs-dp-189876-l3mplsvpn:l3mplsvpn:0-4-th-4270: - Service create(applying template for device PE_10)
```

### Task 2

But of course if we made the change in device not used by our L3VPN service we don't want to redeploy, so we could better refine it.

We could just add a `starts-with(name,'PE_')` to only apply to PE devices, but we know which devices are configured by our service, so let's be precise and refine it to only trigger if PE_00 or PE_10 is modified, using the Kickers `trigger-expr` option

> **NOTE:** Consider that we could include in our service to provision as well a kicker for each service instance, specifically indicating the devices it manages.

To make it easier let's first remember how the xpath to the devices configuration looks like.

```bash
nsoadmin@ncs# show running-config devices device PE_00 config interface GigabitEthernet 0/0 | display xpath
/devices/device[name='PE_00']/config/ios:interface/GigabitEthernet[name='0/0']/vrf/forwarding vpn128
/devices/device[name='PE_00']/config/ios:interface/GigabitEthernet[name='0/0']/ip/address/primary/address 172.17.1.17
/devices/device[name='PE_00']/config/ios:interface/GigabitEthernet[name='0/0']/ip/address/primary/mask 255.255.255.252
nsoadmin@ncs# 
```

And update our kicker with a trigger expression restricting to only trigger kicker if devices are PE_00 or PE_10

```bash
nsoadmin@ncs(config)# do show running-config kickers data-kicker redeploy-l3mplsvpn-on-device-change 
kickers data-kicker redeploy-l3mplsvpn-on-device-change
 monitor     /ncs:devices/ncs:device
 kick-node   /l3mplsvpn:l3mplsvpn
 action-name re-deploy
!
nsoadmin@ncs(config)# kickers data-kicker redeploy-l3mplsvpn-on-device-change
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# trigger-expr "(name = 'PE_00') or (name = 'PE_10')"
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# commit
Commit complete.
nsoadmin@ncs(config-data-kicker-redeploy-l3mplsvpn-on-device-change)# end
nsoadmin@ncs# 
```

Now we can verify it works as expected. First by changing the configuration of a different device, for example PE_01

```bash
nsoadmin@cisco-virtual-machine:~/nso/ncs-run_CLtest$ ncs-netsim cli-c PE_01

User admin last logged in 2024-01-29T12:28:14.199963+00:00, to cisco-virtual-machine, from 127.0.0.1 using cli-ssh
admin connected from 10.227.64.241 using ssh on cisco-virtual-machine
PE_01# config
Entering configuration mode terminal
PE_01(config)# interface GigabitEthernet 0/0 description I was here as well...
PE_01(config-if)# commit
Commit complete.
PE_01(config-if)# 
```

Then we do a sync-from

```
nsoadmin@ncs# devices sync-from
sync-result {
    device PE_00
    result true
}
sync-result {
    device PE_01
    result true
}
sync-result {
    device PE_10
    result true
}
sync-result {
    device PE_11
    result true
}
nsoadmin@ncs# 
```

In devel.log we can see the kicker was not triggered

```log
<INFO> 30-Jan-2024::17:07:34.310 cisco-virtual-machine ncs[189782][<0.16546.0>]: ncs progress usid=82 tid=4325 datastore=running context=cli trace-id=070d33bb-c3b0-4e7e-860f-0eceb8c77fae check data kickers
<INFO> 30-Jan-2024::17:07:34.311 cisco-virtual-machine ncs[189782][<0.16546.0>]: ncs progress usid=82 tid=4325 datastore=running context=cli trace-id=070d33bb-c3b0-4e7e-860f-0eceb8c77fae check data kickers: ok (0.000 s)
```

Now we can modify the configuration in PE_10 that is managed by our service

```bash
nsoadmin@cisco-virtual-machine:~/nso/ncs-run_CLtest$ ncs-netsim cli-c PE_10

User admin last logged in 2024-01-30T16:07:33.088977+00:00, to cisco-virtual-machine, from 127.0.0.1 using cli-ssh
admin connected from 10.227.64.241 using ssh on cisco-virtual-machine
PE_10# config
Entering configuration mode terminal
PE_10(config)# interface GigabitEthernet 0/1 ipv4 address 172.27.1.33 255.255.255.252
PE_10(config-if)# commit
Commit complete.
PE_10(config-if)# end
PE_10# 
```

Then sync-from

```
nsoadmin@ncs# devices device PE_10 sync-from                                               
result true
nsoadmin@ncs# 
```

As before, the l3mplsvpn python vm log shows the re-deploy occurred.

```log

```

```log
<INFO> 02-Feb-2024::00:35:47.182 l3mplsvpn ncs-dp-211277-l3mplsvpn:l3mplsvpn:0-11-th-5896: - Service create(service=/l3mplsvpn:l3mplsvpn{vpn3})
<INFO> 02-Feb-2024::00:35:47.186 l3mplsvpn ncs-dp-211277-l3mplsvpn:l3mplsvpn:0-11-th-5896: - Service create(applying template for device PE_00)
<INFO> 02-Feb-2024::00:35:47.201 l3mplsvpn ncs-dp-211277-l3mplsvpn:l3mplsvpn:0-11-th-5896: - Service create(applying template for device PE_10)
```

Lab Exercise: Converting the L3VPN in a Nano Service
=========================

