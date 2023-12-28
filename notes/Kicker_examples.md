# Example 0: Sync-from on local device-changes

Local changes (in NSO CDB) in a device kick the device sync-from reverting back the changes.

```
nsoadmin@nso1(NCS)(config)# kickers data-kicker sync_XR_on_Loopback_changes monitor /devices/device kick-node . action-name sync-from                                                               
nsoadmin@nso1(NCS)(config-data-kicker-sync_XR_on_Loopback_changes)# show config
kickers data-kicker sync_XR_on_Loopback_changes
 monitor     /devices/device
 kick-node   .
 action-name sync-from
!
nsoadmin@nso1(NCS)(config-data-kicker-sync_XR_on_Loopback_changes)# commit
Commit complete.
nsoadmin@nso1(NCS)(config-data-kicker-sync_XR_on_Loopback_changes)# 
```

Current configuration of Loopback 0 in NSO CDB

```
nsoadmin@nso1(NCS)# show running-config devices device PE_10 config interface Loopback
devices device PE_10
 config
  interface Loopback 0
   ipv4 address 10.1.0.1 /32
   no shutdown
  exit
 !
!
nsoadmin@nso1(NCS)#
```

We make PE_10 out-of-sync by configuring locally the Loopback 1

```
nso1# config
Enter configuration commands, one per line. End with CNTL/Z.
PE_10(config)# interface Loopback 1
PE_10(config-if)# ipv4 address 10.1.0.2 /32
PE_10(config-if)# end
nso1# show running-config interface Loopback
interface Loopback 0
 no shutdown
 ipv4 address 10.1.0.1 /32
exit
interface Loopback 1
 no shutdown
 ipv4 address 10.1.0.2 /32
exit
nso1# nso1# 
```

We update **locally** Loopback 0 description using `no-networking` as device is out-of-sync and we want the transaction to succeed to the kicker is invoked and a sync-from will occur loading the device configuration into NSO CDB

```
nsoadmin@nso1(NCS)# config
Entering configuration mode terminal
nsoadmin@nso1(NCS)(config)# no devices device PE_10 config interface Loopback 0 description I am adding the description only on NSO CDB        
nsoadmin@nso1(NCS)(config)# devices device PE_10 config interface Loopback 0 description I am adding the description only on NSO CDB   
nsoadmin@nso1(NCS)(config-if)# commit     
Aborted: Network Element Driver: device PE_10: out of sync
nsoadmin@nso1(NCS)(config-if)# commit no-networking 
Commit complete.
nsoadmin@nso1(NCS)(config-if)# end
nsoadmin@nso1(NCS)# show running-config devices device PE_10 config interface Loopback
devices device PE_10
 config
  interface Loopback 0
   ipv4 address 10.1.0.1 /32
   no shutdown
  exit
  interface Loopback 1
   ipv4 address 10.1.0.2 /32
   no shutdown
  exit
 !
!
nsoadmin@nso1(NCS)# 
```