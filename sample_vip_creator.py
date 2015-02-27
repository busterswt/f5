#!/usr/bin/env python
import requests, json, sys
from neutronclient.v2_0 import client
from credentials import get_credentials
from tabulate import tabulate

requests.packages.urllib3.disable_warnings()
 
credentials = get_credentials()
 
# Define vars
vip_network_id = 'bcb082fd-1b0a-40d7-9aa1-a5d181d9dbcb'
PROXY_VIP_ADDRESS = '10.240.0.248'
PROXY_USER = 'proxyuser'
PROXY_PASS = 'proxypass'

bigip = requests.session()
bigip.auth = (PROXY_USER, PROXY_PASS)
bigip.verify = False
bigip.headers.update({'Content-Type' : 'application/json'})
##print "created REST resource for BIG-IP at %s..." % PROXY_VIP_ADDRESS

# Requests requires a full URL to be sent as arg for every request, define base URL globally here
BIGIP_URL_BASE = 'https://%s/mgmt/tm' % PROXY_VIP_ADDRESS

def create_http_virtual(bigip, name, address, port, pool):
    payload = {}

    # define test virtual
    payload['kind'] = 'tm:ltm:virtual:virtualstate'
    payload['name'] = name
    payload['description'] = 'Sample Virtual'
    payload['destination'] = '%s:%s' % (address, port)
    payload['mask'] = '255.255.255.255'
    payload['ipProtocol'] = 'tcp'
    payload['sourceAddressTranslation'] = { 'type' : 'automap' }
    payload['profiles'] = [
        { 'kind' : 'ltm:virtual:profile', 'name' : 'http' },
        { 'kind' : 'ltm:virtual:profile', 'name' : 'tcp' }
    ]
    payload['pool'] = pool

    response = bigip.post('%s/ltm/virtual' % BIGIP_URL_BASE, data=json.dumps(payload))
    return response.status_code
    
def create_pool(bigip, name, pool_members, lb_method):
    payload = {}

    # convert member format
    members = [ { 'kind' : 'ltm:pool:members', 'name' : member } for member in pool_members ]

    # define test pool
    payload['kind'] = 'tm:ltm:pool:poolstate'
    payload['name'] = name
    payload['description'] = 'Sample Pool'
    payload['loadBalancingMode'] = lb_method
    payload['monitor'] = 'http'
    payload['members'] = members

    response = bigip.post('%s/ltm/pool' % BIGIP_URL_BASE, data=json.dumps(payload))
    return response.status_code

def create_port():
    credentials = get_credentials()
    neutron = client.Client(**credentials)
 
    body_value = {
                     "port": {
                             "admin_state_up": True,
                             "name": "VIP",
                             "network_id": vip_network_id
                      }
                 }
    response = neutron.create_port(body=body_value)
    #print json.dumps(response, sort_keys=True, indent=4) // Debug Example
    return json.dumps(response["port"]["fixed_ips"][0]["ip_address"])
    
def main():
    vip_addr = create_port()
    
    VS_NAME = "PROXY_VS_" + vip_addr
    VS_ADDRESS = vip_addr
    VS_PORT = "443"
    POOL_NAME = "PROXY_POOL_" + vip_addr
    POOL_LB_METHOD = 'least-connections-member'
    POOL_MEMBERS = [ '10.5.0.1:80', '10.5.0.2:80', '10.5.0.3:80' ]
    
    if (create_pool(bigip, POOL_NAME, POOL_MEMBERS, POOL_LB_METHOD) == 200):
        print "Creating Pool... SUCCESS!"
    else:
    	print "Creating Pool... FAILED"
    	return
    
    if (create_http_virtual(bigip, VS_NAME, VS_ADDRESS, VS_PORT, POOL_NAME) == 200):
    	print "Creating Virtual Server... SUCCESS!"
    else:
        print "Creating Virtual Server... FAILED"
        return
        
    print tabulate([[VS_NAME, VS_ADDRESS, POOL_NAME]],["Virtual Server Name", "Virtual Address", "Pool Name"])

if __name__ == "__main__":
	main()

	
