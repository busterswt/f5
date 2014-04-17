To use this script, you'll need specific /etc/hosts files entries on both the proxy server and the client.

On the client-side:

```/etc/hosts
ip.of.proxy.server f5
```
On the proxy server:
```
/etc/hosts
ip.of.f5.selfip f5
```
The include file contains credentials that allow users to interface with the proxy. It also includes the admin credentials to interface with the F5. This could be made more intelligent later on to allow better control of commands and methods.

To test, execute the following from the client:
```
curl -k -X GET https://user:pass@f5/mgmt/tm/ltm/pool | python -mjson.tool
```
Refer to the F5 ReST API guide at:
https://devcentral.f5.com/d/icontrol-rest-user-guide


###

To sync, this might be the syntax:
https://devcentral.f5.com/questions/rest-api-and-config-sync-question
```
 curl -sk -u admin:admin -H "Content-Type: application/json" -X POST -d '{"command":"run","utilCmdArgs":"config-sync to-group pair-group-name"}' https://x.x.x.x/mgmt/tm/cm
 ```
