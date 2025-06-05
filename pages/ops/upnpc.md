---
title: Port Forwarding with upnpc
---

# Introduction

You may need to configure your Internet router to forward inbound traffic to your Monero Daemon that hosts the blockchain. You can maybe do this by logging into your router and configuring a rule. Alternatively, if your router supports *upnp port forwarding* you can trigger it to create a port forwarding rule using the `upnpc` utility. Note that not all routers support automatic upnp triggering. You may need to login to your router and enable this feature.

# Troubleshooting

If you see a log message like the one below, then you can use the information on this page to solve the problem.

Sample log message:
```
2024-09-29 20:15:33.757 W No incoming connections - check firewalls/routers allow port 20080
```
In the above log message, the Monero Daemon has noted that port 20080 is not receiving any inbound data.

# Installing upnpc

On Debian based systems you can install the upnpc command using apt as shown below.
```
sudo apt install miniupnpc
```
# Adding a Rule

Use the upnpc command to get your router to forward inbound traffic to a particular machine and port number without having to configure your router. 

**NOTE:** You need to run this on the machine that will receive the packets. In the example below, you'll need to run the `upnpc` comand on 192.168.1.2.

```
upnpc -a 192.168.0.169 20080 20080 TCP
```
Sample output from the command above:
```
upnpc : miniupnpc library test client, version 2.2.4.
 (c) 2005-2022 Thomas Bernard.
Go to http://miniupnp.free.fr/ or https://miniupnp.tuxfamily.org/
for more information.
List of UPNP devices found on the network :
 desc: http://192.168.0.1:5000/rootDesc.xml
 st: urn:schemas-upnp-org:device:InternetGatewayDevice:1

Found valid IGD : http://192.168.0.1:5000/ctl/IPConn
Local LAN ip address : 192.168.0.1
ExternalIPAddress = 107.190.99.134
InternalIP:Port = 192.168.0.169:20080
external 107.190.99.134:20080 TCP is redirected to internal 192.168.0.169:20080 (duration=0)
```

The example above forward traffic on port 20080 to 192.168.0.169

# Listing Rules

```
upnpc -l
```

Sample output from the command above:

```
upnpc : miniupnpc library test client, version 2.2.4.
 (c) 2005-2022 Thomas Bernard.
Go to http://miniupnp.free.fr/ or https://miniupnp.tuxfamily.org/
for more information.
List of UPNP devices found on the network :
 desc: http://192.168.0.1:5000/rootDesc.xml
 st: urn:schemas-upnp-org:device:InternetGatewayDevice:1

Found valid IGD : http://192.168.0.1:5000/ctl/IPConn
Local LAN ip address : 192.168.0.176
Connection Type : IP_Routed
Status : Connected, uptime=4468570s, LastConnectionError : ERROR_NONE
  Time started : Mon Apr 14 19:52:18 2025
MaxBitRateDown : 4200000 bps (4.2 Mbps)   MaxBitRateUp 4200000 bps (4.2 Mbps)
ExternalIPAddress = 107.190.99.134
 i protocol exPort->inAddr:inPort description remoteHost leaseTime
 0 TCP 19080->192.168.0.169:19080 'bitmonero' '' 0
 1 TCP 37890->192.168.0.176:37890 'libminiupnpc' '' 0
 2 TCP 38890->192.168.0.176:38890 'P2Pool' '' 0
 3 TCP 37891->192.168.0.122:37891 'P2Pool' '' 0
 4 TCP 21080->192.168.0.122:21080 'bitmonero' '' 0
 5 TCP 20080->192.168.0.176:20080 'bitmonero' '' 0
GetGenericPortMappingEntry() returned 713 (SpecifiedArrayIndexInvalid)
```

# Deleting Rules

```
upnpc -d external_port protocol REMOTE_HOST
```









