#!/usr/bin/python
import requests, json, time

SLEEP_TIME = 20

VS_NAME = 'test-http-virtual_python2'
VS_ADDRESS = '1.1.1.5'
VS_PORT = '80'

POOL_NAME = 'test-http-pool_python2'
POOL_LB_METHOD = 'least-connections-member'
POOL_MEMBERS = [ '10.5.0.1:80', '10.5.0.2:80', '10.5.0.3:80' ]

# create/delete methods
def create_pool(bigip, name, members, lb_method):
    payload = {}

    # convert member format
    members = [ { 'kind' : 'ltm:pool:members', 'name' : member } for member in POOL_MEMBERS ]

    # define test pool
    payload['kind'] = 'tm:ltm:pool:poolstate'
    payload['name'] = name
    payload['description'] = 'A Python REST client test pool'
    payload['loadBalancingMode'] = lb_method
    payload['monitor'] = 'http'
    payload['members'] = members

    bigip.post('%s/ltm/pool' % BIGIP_URL_BASE, data=json.dumps(payload))
    
def create_http_virtual(bigip, name, address, port, pool):
    payload = {}

    # define test virtual
    payload['kind'] = 'tm:ltm:virtual:virtualstate'
    payload['name'] = name
    payload['description'] = 'A Python REST client test virtual server'
    payload['destination'] = '%s:%s' % (address, port)
    payload['mask'] = '255.255.255.255'
    payload['ipProtocol'] = 'tcp'
    payload['sourceAddressTranslation'] = { 'type' : 'automap' }
    payload['profiles'] = [
        { 'kind' : 'ltm:virtual:profile', 'name' : 'http' },
        { 'kind' : 'ltm:virtual:profile', 'name' : 'tcp' }
    ]
    payload['pool'] = pool

    bigip.post('%s/ltm/virtual' % BIGIP_URL_BASE, data=json.dumps(payload))

def delete_pool(bigip, name):
    bigip.delete('%s/ltm/pool/%s' % (BIGIP_URL_BASE, name))

def delete_virtual(bigip, name):
    bigip.delete('%s/ltm/virtual/%s' % (BIGIP_URL_BASE, name))

# REST resource for BIG-IP that all other requests will use
bigip = requests.session()
#bigip.auth = (BIGIP_USER, BIGIP_PASS)
bigip.verify = False
bigip.headers.update({'Content-Type' : 'application/json'})
print "created REST resource for BIG-IP at %s..." % BIGIP_ADDRESS

# Requests requires a full URL to be sent as arg for every request, define base URL globally here
#BIGIP_URL_BASE = 'http://%s/proxy.php/mgmt/tm' % BIGIP_ADDRESS
BIGIP_URL_BASE = 'http://%s/mgmt/tm' % BIGIP_ADDRESS

# create pool
create_pool(bigip, POOL_NAME, POOL_MEMBERS, POOL_LB_METHOD)
print "created pool \"%s\" with members %s..." % (POOL_NAME, ", ".join(POOL_MEMBERS))

# create virtual
create_http_virtual(bigip, VS_NAME, VS_ADDRESS, VS_PORT, POOL_NAME)
print "created virtual server \"%s\" with destination %s:%s..." % (VS_NAME, VS_ADDRESS, VS_PORT)

# sleep for a little while
print "sleeping for %s seconds, check for successful creation..." % SLEEP_TIME
time.sleep(SLEEP_TIME)

# delete virtual
print "deleted virtual server \"%s\"..." % VS_NAME
delete_virtual(bigip, VS_NAME)

# delete pool
print "deleted pool \"%s\"..." % POOL_NAME
delete_pool(bigip, POOL_NAME)
