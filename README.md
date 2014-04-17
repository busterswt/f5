## On the client, set /etc/hosts entry:

ip.of.proxy f5

## On the proxy server, set /etc/hosts entry:

ip.of.f5 f5

###

To sync, this might be the syntax:
https://devcentral.f5.com/questions/rest-api-and-config-sync-question

 curl -sk -u admin:admin -H "Content-Type: application/json" -X POST -d '{"command":"run","utilCmdArgs":"config-sync to-group pair-group-name"}' https://x.x.x.x/mgmt/tm/cm
 
To run it using this proxy, you wouldn't use the credentials (for now)
