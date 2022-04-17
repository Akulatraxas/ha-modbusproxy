# Home Assistant AddOn Modbus Proxy

Allows you to connect multiple clients to one single modbus server. Usally one modbus server only allows a single connection and denies any more clients. 

The addon is only tested and compatible with hassio supervisor. 

## Installation
[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FAkulatraxas%2Fha-modbusproxy)
- Add This [Repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FAkulatraxas%2Fha-modbusproxy) (Or click Button above) 
- Install ModBusProxy from the Add-On Store

## Configuration
- Stop all Clients that currently connect to the modbus server. The Server might need some time before another client (our proxy) can connect.
- Before starting go to the configuration page and set the ip of your modbus server. 
- Start The Add-On
- Configure Your Clients to connect to your HA IP and choosen port.

<img width="382" alt="image" src="https://user-images.githubusercontent.com/103323/163730831-3b757097-c47f-4420-aebe-9fd357b12db4.png">


## Mentions
This addon uses the modbus-proxy of tiagocoutinho:
- https://github.com/tiagocoutinho/modbus-proxy
