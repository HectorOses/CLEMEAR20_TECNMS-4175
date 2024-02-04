TECOPS-2201 - Lab Guide - Implementing Nano Services
====================================

In this task we will modify the simple l3mplsvpn service into a nano service.

Let's imagine that in order to manage the used VPN IDs on L3VPN services there are some operators that are in charge to select and assign that value, and that in the future an external resource manager will be implemented.

However, we decide we don't want to have to ask them for an ID and wait for it, and later to go back and provision the service with it. We want that to be part of the process, so we trigger the service request with all the parameters, and later when they select the ID the service will be automatically deployed.

For this our service now will need at least 2 states, where in the first the request for allocating a VPN ID is triggered, by adding it to a list the operators monitor (we could as well implement in code sending an email or notification) and stop the create there. and the second so when the ID is allocated it will re-deploy our service and configure the devices.

We will need a kicker as well to monitor when the allocation occurs and trigger the re-deploy, but NSO nano-services will create it automatically and delete once it has been satisfied.

After completing this activity, you will be able to:

- Modify an existing service to use ID allocation.
- Transform a service into a nano service.
- Deploy and track the progress of a nano service.

Modify Service Model
-----------------

In this task, you will modify the existing service model in two steps. First, you will create a separate list for the vpn-id allocations for the network operator. Next, you will delete the existing vpn-id leaf.

> **NOTE:** The final solution for this lab is located in the /home/cisco/[PENDING] directory. You can use it for copying and pasting longer pieces of code and as a reference point for troubleshooting your packages.

### Task 1 Define the Nano Service in YANG

Complete these steps:

1. From VS Code terminal or Putty one, as `nsoadmin` user run the make command to ensure the expected packages are loaded for this task

    ```bash
    make [PENDING]
    ```

1. Now we should see the following packages

    ```bash
    [PENDING]
    ```
1. Reload the packages in NSO

    ```bash
    [PENDING]
    ```

1. Check that the packages have been loaded without any issues

    ```bash
    [PENDING]
    ```

1. Use VS Code to open the `l3mplsvpn.yang` file under `packages/l3mplsvpn/src/yang/`.

1. Delete the existing vpn-id leaf.

    ```bash
    < ... Output Omitted ... >

        leaf name {
          tailf:info "Service Instance Name";
          type string;
        }

        leaf vpn-id {
          type uint16;
          tailf:info "Unique VPN ID";
        }

        leaf customer {
          tailf:info "VPN Customer";

    < ... Output Omitted ... >
    ```

1. Create a list vpn-allocations with two leaves vpn-name and vpn-id. Declare vpn-name to be used as a key leaf and use a unique constraint for the vpn-id. Make sure that vpn-name refers to the name leaf located in the l3mplsvpn list.

    ```bash
    < ... Output Omitted ... >
     
    revision 2020-06-04 {
        description
          "Initial revision.";
      }

      list vpn-allocations {
        key "vpn-name";
        unique "vpn-id";

        leaf vpn-name {
          type leafref {
            path /l3mplsvpn/name;
          }
        }

        leaf vpn-id {
          type uint16;
          tailf:info "Unique VPN ID";
        }
      }

    < ... Output Omitted ... >
    ```

1. Save the file and exit the text editor.

#### Task 1 Verification

You have completed this task when you attain these results:

- You have successfully copied a service package
- You have deleted the existing vpn-id leaf
- You have declared a list to store VPN allocations.

Transform the service into a Nano Service
----------------------------

We will now add the required blocks in YANG to define our nano-service, which will consist of three key steps.

First, the service must include the `ncs:nano-plan-data`` grouping which will change the execution model of the service.

Second, the service must define a nano plan declared with the ncs:plan-outline statement. Nano plan definitions consist of plan components and plan state definitions.

[PENDING include here the high level diagram]

Finally, we must define a service behavior tree declared with the ncs:service-behavior-tree statement. The behavior tree is responsible for creating and removing plan components from instances of your service plan.

### Task 2 Transform into a Nano Service

Complete these steps:

1. Open the service model `l3mplsvpn.yang` using VS code. You can find it under `packages/l3mplsvpn/src/yang/l3mplsvpn.yang`

1. Find the l3mplsvpn list definition and declare that `uses` `nano-plan-data`

    ```bash
    < ... Output Omitted ... >

      list l3mplsvpn {
        uses ncs:service-data;
        uses ncs:nano-plan-data;
        ncs:servicepoint l3mplsvpn-servicepoint;
        key name;

    < ... Output Omitted ... >
    ```

1. Declare the plan component and plan state for later use in the plan outline.

    ```bash
    < ... Output Omitted ... >

      revision 2020-06-04 {
        description
          "Initial revision.";
      }

      identity l3mplsvpn {
        base ncs:plan-component-type;
      }

      identity l3mplsvpn-configured {
        base ncs:plan-state;
      } 

      list vpn-allocations {
        key "vpn-name";
        unique "vpn-id";

    < ... Output Omitted ... >
    ```

1. Define your service `plan-outline` and add the mandatory `ncs:self` component with two mandatory states `ncs:init` and `ncs:ready``.

    ```bash
    < ... Output Omitted ... >

      identity l3mplsvpn-configured {
        base ncs:plan-state;
      } 
     
      ncs:plan-outline l3mplsvpn-plan {
        description "L3 MPLS VPN Plan";

        ncs:component-type "ncs:self" {
          ncs:state "ncs:init";
          ncs:state "ncs:ready";
        }
      } 

      list vpn-allocations {
        key "vpn-name";
        unique "vpn-id";

    < ... Output Omitted ... >
    ```

    > **Note:** init and ready states are primarily used as placeholders for timestamps.

1. Define the `l3mplsvpn` `component-type` and define two possible states. However, this time, use the `l3mplsvpn:l3mplsvpn-configured` for the second state declaration.

    You have formally declared these identities previously.

    ```bash
    < ... Output Omitted ... >

      ncs:plan-outline l3mplsvpn-plan {
        description "L3 MPLS VPN Plan";

        ncs:component-type "ncs:self" {
          ncs:state "ncs:init";
          ncs:state "ncs:ready";
        }
        ncs:component-type "l3mplsvpn:l3mplsvpn" {
          ncs:state "ncs:init";
          ncs:state "l3mplsvpn:l3mplsvpn-configured" {
          }
        }
      } 

    < ... Output Omitted ... >
    ```

    >**NOTE:** Consider that our service will trigger frist the `ncs:init` and with it it will add the request of a VPN ID to the list. Then our second state `l3mplsvpn-configured` will wait until the VPN ID is allocated and then trigger a callback to configure the devices

1. Add a create `nano-callback` and define a `pre-condition` inside the block. Write an XPath expression and pass it as an argument to the monitor statement. This will make sure that l3mplsvpn-configured state can be reached only if the monitor condition is satisfied. Make sure you add a `nano-callback` declaration right after the `pre-condition` block.

    ```bash
     < ... Output Omitted ... >
       
      ncs:plan-outline l3mplsvpn-plan {
        description "L3 MPLS VPN Plan";

        ncs:component-type "ncs:self" {
          ncs:state "ncs:init";
          ncs:state "ncs:ready";
        }
        ncs:component-type "l3mplsvpn:l3mplsvpn" {
          ncs:state "ncs:init";
          ncs:state "l3mplsvpn:l3mplsvpn-configured" {
            ncs:create {
              ncs:pre-condition {
                ncs:monitor "/vpn-allocations[vpn-name=$SERVICE/name]/vpn-id";
              }
              ncs:nano-callback;
            }
          }
        }
      }

    < ... Output Omitted ... >
    ```

    >**INFO:** Our plan outline is now defined, but is the `behavior-tree` the one responsible for creating components instantiated from your service plan. You could even use the `component-type` in a different order or skip one in the `behavior-tree`.

1. Write a `behavior-tree` for your service by providing the name of your `service-point` and the name of your `plan-outline`.

    ```bash
    < ... Output Omitted ... >

      ncs:service-behavior-tree l3mplsvpn-servicepoint {
        description "L3 MPLS VPN behavior tree";
        ncs:plan-outline-ref "l3mplsvpn:l3mplsvpn-plan";
        ncs:selector {
          ncs:create-component "'self'" {
            ncs:component-type-ref "ncs:self";
          }
          ncs:create-component "'l3mplsvpn'" {
            ncs:component-type-ref "l3mplsvpn:l3mplsvpn";
          }
        }
      } 

      ncs:plan-outline l3mplsvpn-plan {
        description "L3 MPLS VPN Plan";

    < ... Output Omitted ... >
    ```

1. Save changes and close the file.

1. Open the `l3mplsvpn.py` file in VS code. You can find it under `packages/l3mplsvpn/python/l3mplsvpn/l3mplsvpn.py`.

    ```bash
    student@student-vm:~/nso300$ vim packages/l3mplsvpn/python/l3mplsvpn/l3mplsvpn.py
    ```

1. Delete the highlighted ServiceCallbacks class declaration, `@Service.create decorator`, and `cb_create` method declaration along with the call to the `self.log.debug method.

1. Nano services require class inheritance from a different class than standard services.

    ```bash
    import ncs
    import math

    class ServiceCallbacks(ncs.application.Service):

        @Service.create
        def cb_create(self, tctx, root, service, proplist):
            self.log.info('Service create(service=', service._path, ')')

    < ... Output Omitted ... >
    ```

1. Declare a `class L3MPLSNanoService`, which inherits from the ncs.application.NanoService class. Use the @ncs.application.NanoService.create decorator and define the cb_nano_create method with a call to the self.log.debug method.

    ```bash
    import ncs
    import math

    class L3MPLSNanoService(ncs.application.NanoService):

        @ncs.application.NanoService.create
        def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
            self.log.debug("NanoService create ", state)

    < ... Output Omitted ... >
    ```

    >**Note:** `cb_nano_create` accepts additional parameters—plan, component, state, and component_proplist.

1. Delete the line with the vpn_id declaration. Remember that your service model no longer provides the vpn-id.

    ```bash
    < ... Output Omitted ... >

           vpn_id = service.vpn_id

    < ... Output Omitted ... >
    ```

1. Add lines to obtain vpn-id from vpn-allocations list, and a call to `self.log.info` method. Make sure that you use **underscores** and not hyphen when declaring variables.

    ```bash
    < ... Output Omitted ... >

            self.log.debug("NanoService create ", state)

            vpn_id = root.vpn_allocations[service.name].vpn_id
            self.log.info(f'Vpn ID read: {vpn_id}')

    < ... Output Omitted ... >
    ```

1. Scroll down to near the end of the file and add a return proplist statement. Also, add a call to self.`register_nano_service` with your service parameters.

    ```bash
    < ... Output Omitted ... >
          
                template.apply('l3mplsvpn-template', tvars)

            return proplist

    # ---------------------------------------------
    # COMPONENT THREAD THAT WILL BE STARTED BY NCS.
    # ---------------------------------------------
    class L3MplsVpn(ncs.application.Application):
        def setup(self):
            self.log.info('L3MplsVpn RUNNING')
            self.register_nano_service('l3mplsvpn-servicepoint', 'l3mplsvpn:l3mplsvpn', 'l3mplsvpn:l3mplsvpn-configured', L3MPLSNanoService)

        def teardown(self):
            self.log.info('L3MplsVpn FINISHED')                          

    < ... Output Omitted ... >
    ```

1. Save changes.

    Compile and deploy your package.

    student@student-vm:~/nso300$ make testenv-build

    ```bash
    < ... Output Omitted ... >

    -- Reloading packages for NSO testenv-nso300-5.3.2-student-nso
    reload-result {
        package cisco-asa-cli-6.10
        result true
    }
    reload-result {
        package cisco-ios-cli-6.54
        result true
    }
    reload-result {
        package cisco-iosxr-cli-7.26
        result true
    }
    reload-result {
        package cisco-nx-cli-5.15
        result true
    }
    reload-result {
        package l3mplsvpn
        result true
    }

    < ... Output Omitted ... >
    ```

#### Task 2 Verification

You have completed this task when you attain these results:

- You have successfully transformed the service into a nano service.
- You have successfully built the nano service package.

### Task 3 Deploy Nano Services

In this task, you will deploy the newly created nano service.
Activity

Complete these steps:

1. Enter the NSO CLI and switch to the Cisco mode.

    ```bash
    student@student-vm:~/nso300$ make testenv-cli
    docker exec -it testenv-nso300-5.3.2-student-nso bash -lc 'ncs_cli -u admin'

    admin connected from 127.0.0.1 using console on ebdb0d8aa9a2
    nsoadmin@ncs> switch cli
    nsoadmin@ncs#
    ```

1. Enter the configuration mode and create a new customer entry called ACME (if not existing already).

    ```bash
    nsoadmin@ncs# config
    Entering configuration mode terminal
    nsoadmin@ncs(config)# customers customer ACME
    nsoadmin@ncs(config-customer-ACME)#
    ```

1. Commit the configuration and return to the top.

    ```bash
    nsoadmin@ncs(config-customer-ACME)# commit
    Commit complete.
    nsoadmin@ncs(config-customer-ACME)# top
    nsoadmin@ncs(config)#
    ```

1. Configure a new VPN service instance for the new customer and name it vpn512.

    ```bash
    nsoadmin@ncs(config)# l3mplsvpn vpn512 customer ACME
    nsoadmin@ncs(config-l3mplsvpn-vpn512)#
    ```

1. Configure two links, each on a different device.

    ```bash
    nsoadmin@ncs(config-l3mplsvpn-vpn512)# link 1 device PE_00 interface 0/1
    nsoadmin@ncs(config-link-1)# exit
    nsoadmin@ncs(config-l3mplsvpn-vpn512)# link 2 device PE_10 interface 0/2
    nsoadmin@ncs(config-link-2)# exit
    nsoadmin@ncs(config-l3mplsvpn-vpn512)# 
    ```

1. Commit the configuration and exit configuration mode.

    ```bash
    nsoadmin@ncs(config-l3mplsvpn-vpn512)# commit
    Commit complete.
    nsoadmin@ncs(config-l3mplsvpn-vpn512)# end
    nsoadmin@ncs#
    ```

1. Inspect the status of the newly configured service instance.

    Plan component l3mplsvpn has not reached the l3mplsvpn-configured state because a pre-condition exists, which requires the presence of a vpn-id value in the vpn-allocations list.

    ```bash
    nsoadmin@ncs# show l3mplsvpn vpn512
                                                                                                    POST
                          BACK                                                                      ACTION
    TYPE       NAME       TRACK  GOAL  STATE                 STATUS       WHEN                 ref  STATUS
    --------------------------------------------------------------------------------------------------------
    self       self       false  -     init                  reached      2020-09-15T18:10:11  -    -
                                       ready                 reached      2020-09-15T18:10:11  -    -
    l3mplsvpn  l3mplsvpn  false  -     init                  reached      2020-09-15T18:10:11  -    -
                                       l3mplsvpn-configured  not-reached  -                    -    -

    nsoadmin@ncs#
    ```

    > **Note:** The NSO CLI adapts the output to the width of your terminal window. In case your window is too narrow, you can use the <command> | tab format, to force the NSO CLI to display the tabulated output.

1. Enter the configuration mode.

    ```bash
    nsoadmin@ncs# config
    Entering configuration mode terminal
    nsoadmin@ncs(config)#
    ```

1. Use the vpn-allocations command to allocate a new vpn-id to the service instance.

    You are taking the role of a network operator that is acting upon a new VPN service request.

    ```bash
    nsoadmin@ncs(config)# vpn-allocations ?
    Possible completions:
      vpn512
    nsoadmin@ncs(config)# vpn-allocations vpn512 vpn-id 512
    nsoadmin@ncs(config-vpn-allocations-vpn512)#
    ```

1. Commit the configuration and exit the configuration mode.

    ```bash
    nsoadmin@ncs(config-vpn-allocations-vpn512)# commit
    Commit complete.
    nsoadmin@ncs(config-vpn-allocations-vpn512)# end
    nsoadmin@ncs#
    ```

1. Display the status of the service instance vpn512 one more time.

    Notice that the plan component l3mplsvpn has now reached the l3mplsvpn-configured state after the pre-condition was satisfied.

    ```bash
    nsoadmin@ncs# show l3mplsvpn vpn512
    l3mplsvpn vpn512
     modified devices [ PE_10 ]
     directly-modified devices [ PE_10 ]
     device-list [ PE_10 ]
                                                                                                POST
                          BACK                                                                  ACTION
    TYPE       NAME       TRACK  GOAL  STATE                 STATUS   WHEN                 ref  STATUS
    ----------------------------------------------------------------------------------------------------
    self       self       false  -     init                  reached  2020-09-15T18:10:11  -    -
                                       ready                 reached  2020-09-15T18:10:11  -    -
    l3mplsvpn  l3mplsvpn  false  -     init                  reached  2020-09-15T18:10:11  -    -
                                       l3mplsvpn-configured  reached  2020-09-15T18:11:53  -    -

    nsoadmin@ncs# 
    ```

#### Task 3 Verification

You have completed this task when you attain these results:

- You have successful configured service instance.
- Your plan component l3mplsvpn has reached l3mplsvpn-configured state.
