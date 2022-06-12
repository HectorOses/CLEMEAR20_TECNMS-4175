

Device Manager
------------------

Cisco VS Juniper CLI Style

```
show devices list
show running-config devices device PE_00
```

33.

Make device PE_00 out-of-sync with NSO CDB

```
config
devices device PE_00 config interface Loopback 0
ip address 10.0.0.11 255.255.255.255
commit no-networking 
end
```

Testing check-sync, sequencial and parallel

```
devtools true
timecmd devices device PE_00 check-sync
timecmd devices check-sync
timecmd devices device PE_* check-sync
timecmd devices check-sync device [ PE_00 PE_01 PE_10 PE_11 PE_20 PE_21 ]
```

Testing compare-config

```
devices device PE_00 compare-config
devices device PE_00 sync-from
```

37.

Exploring devices configuration

```
show running-config devices device PE_00 config interface Loopback 0
```

Unified CLI for multi-vendor devices

```
show running-config devices device PE_10 config interface Loopback 0
```

37.

Configuring a device

```
config
devices device PE_00 config iinterface Loopback 20
ip address 10.2.2.2 255.255.255.255
devices device PE_00 config interface Loopback 30
ip address 10.3.3.3 255.255.255.255
show configuration
```

```
top
show config
```

Commit & Dry-run

```
commit dry-run
commit dry-run outformat native
commit dry-run outformat XML
```

```
commit
```

39.

#### Load Merge terminal

```
config
load merge terminal
```

```
devices device PE_10
 config
  interface Loopback 20
   ipv4 address 10.4.4.4 /32
   no shutdown
  exit
  interface Loopback 30
   ipv4 address 10.5.5.5 /32
   no shutdown
  exit
 !
!
```

Ctrl+D

```
show config
abort
```

#### Save & Load Merge File

```
show configuration | save xr_loopback
abort
config
load merge xr_loopback
show config
```

FastMap
--------------

104. End of Fastmap

```
Load merge l2vpn_exampleA.txt
show config
```

```
show running-config devices device ISR4K_0 config interface Loopback | display service-meta-data
```

```
load merge l2vpn_example_Fastmap.txt
show config
commit
```

```
show running-config devices device ISR4K_0 config interface Loopback | display service-meta-data
```

```
no services l2vpn ABC_TEST
commit dry-run
commit
show running-config devices device ISR4K_0 config interface Loopback | display service-meta-data
```

42.

Rollback
------------

From Linux terminal:

```
ls -lrt logs/rollback*
cat logs/rollback100xx
```

From NSO:
```
show configuration commit list
show configuration commit changes 100xx
show configuration rollback changes 100XX
```

43.

```
rollback configuration 100xx
show config
rollback configuration 100xx-1
show config
rollback selective 100xx-1
show config
rollback configuration 10016 devices device PE_10 config interface Loopback 20
show config
```

```
rollback configuration 10016
show config
commit
```
