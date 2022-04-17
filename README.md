# Home Assistant AddOn Modbus Proxy

Allows you to connect multiple clients to one single modbus server. Usally one server only allows a single connection

## Installation

## Configuration
- Stop all Clients that currently connect to the modbus server. The Server might need some time before another client (our proxy) can connect.
- Before starting go to the configuration page and set the ip of your modbus server. 
- Start The Add-On
- Configure Your Clients to connect to your HA IP and choosen port.

<img width="382" alt="image" src="https://user-images.githubusercontent.com/103323/163730831-3b757097-c47f-4420-aebe-9fd357b12db4.png">


## Mentions
This addon uses the modbus-proxy of tiagocoutinho:
- https://github.com/tiagocoutinho/modbus-proxy
