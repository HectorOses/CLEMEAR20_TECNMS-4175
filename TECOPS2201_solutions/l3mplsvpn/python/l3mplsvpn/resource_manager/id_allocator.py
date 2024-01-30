from . import rm_id_alloc


def id_request(service, svc_xpath, username, pool_name, allocation_name,
                sync,requested_id=-1 ,redeploy_type="default",alloc_sync=False,root=None):
    """Create an allocation request.

    After calling this function, you have to call response_ready
    to check the availability of the allocated ID.

    Example:
    import resource_manager.id_allocator as id_allocator
    pool_name = "The Pool"
    allocation_name = "Unique allocation name"

    # This will try to allocate the value 20 from the pool named 'The Pool'
    # using allocation name: 'Unique allocation name'
    id_allocator.id_request(service,
                            "/services/vl:loop-python[name='%s']" % (service.name),
                            tctx.username,
                            pool_name,
                            allocation_name,
                            False,
                            20)


    id = id_allocator.id_read(tctx.username, root,
                              pool_name, allocation_name)

    if not id:
        self.log.info("Alloc not ready")
        return

    print ("id = %d" % (id))

    The redeploy_type argument sets the redeploy type used by the Resource
    Manager to redeploy the service. The allowed values:
    - touch
    - re-deploy
    - reactive-re-deploy
    - default: chooses one of the previous options based on the NSO version.

    Arguments:
    service -- the requesting service node
    svc_xpath -- xpath to the requesting service
    username -- username to use when redeploying the requesting service
    pool_name -- name of pool to request from
    allocation_name -- unique allocation name
    sync -- sync allocations with this name across pools
    requested_id -- a specific ID to be requested
    redeploy_type -- service redeploy action: default, touch, re-deploy, reactive-re-deploy
    """
    try:
        if alloc_sync:
            rm_id_alloc.id_request_sync(root, service, username, pool_name, allocation_name,
                     sync,requested_id)
        
        rm_id_alloc.id_request_async(service, svc_xpath, username, pool_name, allocation_name,
                       sync,alloc_sync, requested_id, redeploy_type)
    except Exception:
        raise

def id_read(username, root, pool_name, allocation_name):
    """Returns the allocated ID or None

    Arguments:
    username -- the requesting service's transaction's user
    root -- a maagic root for the current transaction
    pool_name -- name of pool to request from
    allocation_name -- unique allocation name
    """

    # Look in the current transaction
    alloc = root.ralloc__resource_pools.idalloc__id_pool[pool_name].allocation[allocation_name]
    if alloc.response.id:
        return str(alloc.response.id)
    elif alloc.response.error:
        raise LookupError(alloc.response.error)
    else:
        return rm_id_alloc.id_read_async(username, root, pool_name, allocation_name)
