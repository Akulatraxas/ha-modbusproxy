# Home Assistant Add-on: Modbus Proxy

[![License][license-shield]](LICENSE)

A powerful multi-device Modbus TCP proxy for Home Assistant with enhanced logging and client tracking. Allows multiple clients to connect to Modbus servers that typically only support a single connection.

## ⚠️ BETA VERSION WARNING

**This is a BETA version (2.2.1-beta) with experimental RTU/Serial and RTU over TCP support.**

**⚠️ Important Notes:**
- **Experimental Features**: RTU/Serial and RTU over TCP support is still being tested
- **Backup Recommended**: Backup your current configuration before testing
- **Fallback Available**: You can always switch back to stable version 2.1.0
- **Testing Phase**: This version is for testing RTU devices only
- **Community Testing Needed**: RTU and RTU over TCP features need real-world testing

**To install Beta version:**
1. Go to [GitHub Releases](https://github.com/TCzerny/ha-modbusproxy/releases)
2. Download the `v2.2.1-beta` release
3. Install as local add-on in Home Assistant

**To switch back to stable version:**
1. Remove the beta add-on
2. Add the repository: `https://github.com/TCzerny/ha-modbusproxy`
3. Install the stable version

**Note:** The Supervisor automatically installs the latest stable version.
Beta versions must be installed manually from GitHub Releases.

## 🧪 Community Testing Needed

**We need your help to test RTU features!**

This beta version includes experimental RTU/Serial and RTU over TCP support that needs real-world testing. If you have:

- **RTU/Serial Devices**: USB-to-Serial adapters, RS485 devices, energy meters, sensors
- **RTU over TCP Gateways**: Network devices that provide RTU over TCP access
- **Willingness to test**: Help us validate these features in real environments

**Please help us by:**
1. Testing RTU/Serial connections with your devices
2. Testing RTU over TCP connections if you have compatible gateways
3. Reporting issues, successes, or suggestions
4. Sharing configuration examples that work

**Report your testing results:**
- ✅ **Success stories**: What devices work well
- ❌ **Issues**: Problems you encounter
- 💡 **Suggestions**: Improvements you'd like to see
- 📋 **Configurations**: Working setup examples

Create an issue on GitHub or join the discussion to help make these features stable!

## 🆕 What's New in Version 2.2.1-beta

**RTU/Serial Modbus Support:**
- 🔌 **RTU Protocol Support**: Connect to Modbus RTU devices via serial ports
- 🌐 **RTU over TCP Support**: Connect to Modbus RTU devices over TCP network (`rtutcp://` scheme)
- 📡 **Serial Communication**: Support for USB-to-Serial adapters and RS485 devices
- ⚙️ **Configurable Serial Parameters**: Baudrate, databits, stopbits, parity
- 🔍 **Enhanced INFO Messages**: Clear Client ↔ Proxy ↔ Device tracking
- 🔍 **Auto-Detection**: Automatically detect serial devices for plug & play setup

**Enhanced Logging & Debug Features:**
- 🔍 **Client IP Tracking**: Every log entry shows the client's IP address and port
- 📊 **Debug Value Parsing**: At DEBUG level, see actual Modbus register values and coil states
- 🎯 **Detailed Request/Response Logging**: Transaction IDs, Unit IDs, Function Codes
- ⚡ **Performance Monitoring**: Response times and connection statistics
- 🔍 **Enhanced INFO Messages**: Clear Client ↔ Proxy ↔ Device tracking
- 📈 **Request Counting**: Track number of requests per client connection

**Example Debug Output (TCP):**
```
2024-12-19 10:30:16 DEBUG Client(192.168.1.50:45231): received request from 192.168.1.50:45231 - 12 bytes
2024-12-19 10:30:16 DEBUG Client(192.168.1.50:45231): received_from_client: TxID=1, Unit=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(192.168.1.100:502): Registers: [12345, 67890, 11111, 22222]
```

**Example Debug Output (RTU):**
```
2024-12-19 10:30:16 DEBUG ModBus(RTU:/dev/ttyUSB0): received RTU 8 bytes: b'010300010001C40A'
2024-12-19 10:30:16 DEBUG ModBus(RTU:/dev/ttyUSB0): received RTU: Slave=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(RTU:/dev/ttyUSB0): RTU Registers: [12345]
```

**Example Debug Output (RTU over TCP):**
```
2024-12-19 10:30:16 DEBUG ModBus(RTUoverTCP:192.168.1.200:502): received RTU 8 bytes: b'010300010001C40A'
2024-12-19 10:30:16 DEBUG ModBus(RTUoverTCP:192.168.1.200:502): received RTU: Slave=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(RTUoverTCP:192.168.1.200:502): RTU Registers: [12345]
```

## About

Most Modbus TCP servers only allow a single client connection and reject additional clients. This add-on creates a proxy that can handle multiple client connections simultaneously while maintaining a single connection to each Modbus server.

**Key Features:**
- 🔄 Multiple client connections to single Modbus server
- 🌐 Support for multiple Modbus devices (TCP, RTU, and RTU over TCP)
- ⚙️ Easy configuration through Home Assistant UI
- 🔧 Configurable timeouts and connection parameters
- 📊 Enhanced logging with client tracking and debug value parsing
- 🚀 Host network mode for optimal performance
- 🔍 Real-time client IP monitoring and request tracking
- 🔌 RTU/Serial Modbus support with configurable serial parameters
- 🌐 **RTU over TCP**: Connect to RTU devices over network using `rtutcp://` scheme
- 🔍 **Auto-Detection**: Plug & play serial device detection
- ⚡ **Asyncio Serial**: Non-blocking serial communication
- 🛡️ **Udev Integration**: Automatic device permissions
- 📈 **Request Counting**: Track requests per client connection

## Installation

### Method 1: One-Click Installation (Recommended)

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FTCzerny%2Fha-modbusproxy)

### Method 2: Manual Installation

1. Navigate to **Settings** → **Addons** → **Add-on Store** in your Home Assistant
2. Click the **⋮** menu in the top right corner
3. Select **Repositories**
4. Add this repository URL: `https://github.com/TCzerny/ha-modbusproxy`
5. Find **Modbus Proxy** in the add-on store
6. Click **Install**

## Configuration

### Basic Configuration Example

```yaml
- name: "Solar Inverter"
  host: "192.168.1.100"
  bind_port: 502
```

### Configuration Parameters

#### TCP Modbus Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | No | `Device X` | Friendly name for the device |
| `host` | **Yes** (for TCP) | - | IP address of the Modbus server |
| `port` | No | `502` | Modbus TCP port of the server |
| `bind_port` | **Yes** | - | Local port where proxy will listen |
| `unit_id_remapping` | No | - | Map incoming unit ID to target unit ID (e.g., `1: 10`) |
| `connection_time` | No | `0.1` | Time to establish connection in seconds |
| `log_level` | No | `info` | Logging level: `debug`, `info`, `warning`, `error` |

#### RTU/Serial Modbus Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | No | `Device X` | Friendly name for the device |
| `protocol` | No | Auto-detected | Protocol type: `tcp` or `rtu` |
| `device` | No* | - | Serial device path (e.g., `/dev/ttyUSB0`) |
| `baudrate` | No | `9600` | Serial baudrate |
| `databits` | No | `8` | Number of data bits |
| `stopbits` | No | `1` | Number of stop bits |
| `parity` | No | `N` | Parity: `N` (None), `E` (Even), `O` (Odd) |
| `bind_port` | **Yes** | - | Local port where proxy will listen |
| `unit_id_remapping` | No | - | Map incoming unit ID to target unit ID |
| `timeout` | No | `5.0` | Connection timeout in seconds |
| `connection_time` | No | `0.1` | Time to establish connection in seconds |
| `log_level` | No | `info` | Logging level: `debug`, `info`, `warning`, `error` |

*`device` is optional when `auto_detect_device: true` is enabled

**Protocol Detection:**
- **Explicit Protocol**: Use `protocol: "tcp"`, `protocol: "rtu"`, or `protocol: "rtutcp"`
- **Auto-Detection**: If no protocol is specified:
  - `host` parameter → TCP Modbus
  - `device` parameter → RTU/Serial Modbus
  - Both `host` and `device` → Use explicit `protocol` field

#### RTU over TCP Modbus Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | No | `Device X` | Friendly name for the device |
| `protocol` | **Yes** | - | Must be set to `rtutcp` for RTU over TCP |
| `host` | **Yes** | - | IP address of the RTU over TCP server |
| `port` | No | `502` | RTU over TCP port of the server |
| `bind_port` | **Yes** | - | Local port where proxy will listen |
| `unit_id_remapping` | No | - | Map incoming unit ID to target unit ID |
| `timeout` | No | `5.0` | Connection timeout in seconds |
| `connection_time` | No | `0.1` | Time to establish connection in seconds |
| `log_level` | No | `info` | Logging level: `debug`, `info`, `warning`, `error` |

### Auto-Detection Configuration

The add-on can automatically detect serial devices for plug & play setup:

```yaml
# Enable auto-detection
auto_detect_device: true

modbus_devices:
  - name: "Auto-Detected Solar Inverter"
    protocol: "rtu"
    baudrate: 9600
    databits: 8
    stopbits: 1
    parity: "N"
    bind_port: 502
    timeout: 5.0
    connection_time: 0.1
```

**Auto-Detection Priority:**
1. `/dev/serial/by-id/*` - Stable device identifiers
2. `/dev/ttyUSB0` - Common USB-to-Serial adapter
3. `/dev/ttyACM0` - Arduino/ACM devices
4. Any `/dev/ttyUSB*` or `/dev/ttyACM*` device

**Benefits:**
- 🔌 **Plug & Play**: No manual device path configuration
- 🔄 **Hot-Swappable**: Automatically adapts to device changes
- 🛡️ **Error Prevention**: Reduces configuration mistakes
- ⚡ **Quick Setup**: Faster initial configuration

### Advanced Configuration Examples

#### Unit ID Remapping

The `unit_id_remapping` feature allows you to map incoming unit IDs to different target unit IDs on the Modbus server. This is useful when:

- Your Modbus client expects a specific unit ID (e.g., 1)
- The actual Modbus server has the device on a different unit ID (e.g., 10)
- You want to virtualize unit IDs for different clients

**Syntax:** `unit_id_remapping: "1<>10"` means:
- When a client sends a request to unit ID 1, it gets forwarded to unit ID 10 on the server
- All responses from unit ID 10 appear as if they came from unit ID 1

**Multiple Mappings:** `unit_id_remapping: "1<>10,2<>20,3<>30"` for multiple unit ID mappings

**JSON Syntax (Legacy):** `unit_id_remapping: "{\"1\": 10}"` - still supported for backward compatibility

**Note:** Each device can only have one remapping configuration.

#### Multiple Solar Inverters with Unit ID Remapping
```yaml
modbus_devices:
  - name: "Inverter 1"
    host: "192.168.1.100"
    port: 502
    bind_port: 503
    unit_id_remapping: "1<>10"
    timeout: 10.0
    connection_time: 2.0
  - name: "Inverter 2"
    host: "192.168.1.101"
    bind_port: 504
    timeout: 10.0
    connection_time: 2.0
  - name: "Inverter 3"
    host: "192.168.1.102"
    bind_port: 505
log_level: "info"
```

#### Mixed TCP, RTU, and RTU over TCP Devices
```yaml
modbus_devices:
  - name: "TCP Solar Inverter"
    host: "192.168.1.100"
    port: 502
    bind_port: 502
    timeout: 10.0
    connection_time: 2.0
  - name: "RTU Energy Meter"
    device: "/dev/ttyUSB0"
    baudrate: 9600
    databits: 8
    stopbits: 1
    parity: "N"
    bind_port: 503
    timeout: 5.0
    connection_time: 1.0
  - name: "RTU over TCP Gateway"
    protocol: "rtutcp"
    host: "192.168.1.200"
    port: 502
    bind_port: 504
    timeout: 5.0
    connection_time: 1.0
  - name: "RTU Temperature Sensor"
    device: "/dev/ttyACM0"
    baudrate: 115200
    databits: 8
    stopbits: 1
    parity: "E"
    bind_port: 505
    timeout: 3.0
    connection_time: 0.5
log_level: "debug"
```
<img width="1027" height="727" alt="image" src="https://github.com/user-attachments/assets/cdafcf9b-c521-4acb-a628-902217242466" />

## Usage

### Step 1: Stop Existing Clients
Before starting the proxy, stop all clients currently connected to your Modbus servers. The server needs time to release existing connections.

### Step 2: Configure the Add-on
1. Go to **Settings** → **Addons** → **Modbus Proxy**
2. Click the **Configuration** tab
3. Add your Modbus devices using the examples above
4. Click **Save**

### Step 3: Start the Add-on
1. Click the **Info** tab
2. Click **Start**
3. Monitor the logs for successful connections

### Step 4: Update Your Clients
Configure your Modbus clients to connect to:
- **Host:** Your Home Assistant IP address
- **Port:** The `bind_port` you configured for each device

## Troubleshooting

### Common Issues

#### "Address already in use" Error
```
OSError: [Errno 98] error while attempting to bind on address ('0.0.0.0', 502): address in use
```
**Solution:** Change the `bind_port` to an unused port (e.g., 505, 506, etc.)

#### "Connection refused" Error
```
Connection refused to 192.168.1.100:502
```
**Solutions:**
1. Verify the Modbus server IP address and port
2. Ensure the Modbus server is running and accessible
3. Check firewall settings on both devices
4. Stop other clients connected to the Modbus server

#### "Timeout" Errors
**Solutions:**
1. Increase the `timeout` value in configuration
2. Increase the `connection_time` value
3. Check network connectivity and latency

#### Master-Slave Inverter Connection Issues
**Problem:** Second inverter (slave) connection fails in Master-Slave setups (e.g., Sungrow hybrid inverters)

**Related Issue:** [#4 - Connection to second inverter fails](https://github.com/TCzerny/ha-modbusproxy/issues/4)

**Symptoms:**
- First inverter connects successfully
- Second inverter shows connection errors
- Timeout or connection refused errors

**Solutions:**
1. **Reduce `connection_time`** - Set to `0.1` or `0.0` for faster connection establishment
2. **Increase `timeout`** - Set to `15.0` or higher for slower responding devices
3. **Check inverter settings** - Ensure both inverters are properly configured for Master-Slave mode
4. **Network delays** - Some inverters need time between connection attempts

**Recommended Configuration for Master-Slave:**
```yaml
modbus_devices:
  - name: "Master Inverter"
    host: "192.168.1.100"
    port: 502
    bind_port: 502
    timeout: 15.0
    connection_time: 0.1  # Reduced for faster connection
  - name: "Slave Inverter"
    host: "192.168.1.101"
    port: 502
    bind_port: 503
    timeout: 15.0
    connection_time: 0.1  # Reduced for faster connection
```

### Enhanced Logging & Monitoring

The add-on provides multiple logging levels for different monitoring needs:

#### Logging Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **`debug`** | Detailed Modbus parsing | See actual register values and function codes |
| **`info`** | Connection status | Basic connection and error information |
| **`warning`** | Warnings only | Important issues that don't break functionality |
| **`error`** | Errors only | Critical problems only |

#### INFO Level - Connection Status

Perfect for monitoring which devices connect to your proxy and their status:

```yaml
log_level: "info"
```

**Example INFO Output:**
```
2024-12-19 10:30:15 INFO modbus-proxy.ModBus - Ready to accept requests on 0:502 for Device(192.168.1.100:502)
2024-12-19 10:30:16 INFO modbus-proxy.Client - new client connection from 192.168.1.50:45231 -> to Proxy
2024-12-19 10:30:16 INFO modbus-proxy.ModBus - connecting Proxy to Modbus Device(192.168.1.100:502)...
2024-12-19 10:30:16 INFO modbus-proxy.ModBus - connected to Device(192.168.1.100:502)!
```

**Example INFO Output (RTU):**
```
2024-12-19 10:30:15 INFO modbus-proxy.ModBus - Ready to accept requests on 0:503 for Device(/dev/ttyUSB0)
2024-12-19 10:30:16 INFO modbus-proxy.Client - new client connection from 192.168.1.51:45232 -> to Proxy
2024-12-19 10:30:16 INFO modbus-proxy.ModBus - connecting to RTU device /dev/ttyUSB0...
2024-12-19 10:30:16 INFO modbus-proxy.ModBus - connected to RTU device /dev/ttyUSB0!
```

#### DEBUG Level - Detailed Modbus Parsing

For detailed analysis of Modbus messages and values:

```yaml
log_level: "debug"
```

**What you'll see in DEBUG mode:**
- **Client Connections**: `Client(192.168.1.50:45231): new client connection from 192.168.1.50:45231`
- **Request Details**: `received_from_client: TxID=1, Unit=1, FC=03` (Transaction ID, Unit ID, Function Code)
- **Response Values**: `Registers: [12345, 67890, 11111, 22222]` or `Values: [1, 0, 1, 1, 0, 1]`
- **Performance**: Response times and connection statistics

**Check the add-on logs:**
1. Go to **Settings** → **Addons** → **Modbus Proxy**
2. Click the **Log** tab
3. Look for detailed client tracking and modbus value information

**Example Debug Session:**
```
2024-12-19 10:30:15 INFO Client(192.168.1.50:45231): new client connection from 192.168.1.50:45231
2024-12-19 10:30:16 DEBUG Client(192.168.1.50:45231): received request from 192.168.1.50:45231 - 12 bytes
2024-12-19 10:30:16 DEBUG Client(192.168.1.50:45231): received_from_client: TxID=1, Unit=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(192.168.1.100:502): sent_to_device: TxID=1, Unit=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(192.168.1.100:502): received: TxID=1, Unit=1, FC=03
2024-12-19 10:30:16 DEBUG ModBus(192.168.1.100:502): Registers: [12345, 67890, 11111, 22222]
2024-12-19 10:30:16 INFO Client(192.168.1.50:45231): Response: 15 bytes, 45.2ms
```

### RTU/Serial Configuration

**⚠️ BETA WARNING: RTU features are experimental and need testing!**

**Important Notes for RTU Devices:**
- 🔌 **Serial Port Access**: The add-on needs access to serial ports on the host
- 📁 **Device Paths**: Common paths are `/dev/ttyUSB0`, `/dev/ttyACM0`, `/dev/ttyS0`
- 🔧 **Permissions**: Automatic permission handling with udev integration
- 📊 **Baudrate**: Must match your device's communication speed
- 🔄 **Parity**: Common values are `N` (None), `E` (Even), `O` (Odd)
- ⚡ **Asyncio Support**: Non-blocking serial communication for better performance
- 🧪 **Testing Needed**: Please report your RTU device testing results

**Enhanced Features:**
- 🔍 **Auto-Detection**: Automatically find and configure serial devices
- 🛡️ **Udev Rules**: Automatic permission setting for USB-Serial adapters
- ⚡ **Asyncio Serial**: Improved performance with non-blocking I/O
- 🔄 **Hot-Plug**: Support for device hot-swapping
- 📈 **Request Tracking**: Monitor serial communication activity

**Troubleshooting RTU Connections:**
- Check if the serial device exists: `ls -la /dev/tty*`
- Verify device permissions: `ls -la /dev/ttyUSB0`
- Test serial communication: `stty -F /dev/ttyUSB0 9600`
- Check for device conflicts: `dmesg | grep tty`
- Monitor auto-detection: Check logs for "Auto-detecting serial device"

### Technical Improvements

**Enhanced Serial Communication:**
- ⚡ **Asyncio Serial**: Non-blocking serial I/O using `pyserial-asyncio`
- 🔄 **Fallback Support**: Graceful fallback to synchronous serial if needed
- 🛡️ **Permission Management**: Automatic device permission handling
- 🔍 **Device Validation**: Comprehensive device existence and permission checks

**Udev Integration:**
- 🔧 **Automatic Permissions**: udev rules for common USB-Serial adapters
- 🔌 **Hot-Plug Support**: Automatic device detection and configuration
- 🛡️ **Permission Fixing**: Attempts to fix device permissions automatically
- 📋 **Device Mapping**: Support for `/dev/serial/by-id/` stable identifiers

**Enhanced Error Handling:**
- 🔍 **Device Validation**: Checks device existence and permissions
- 🛡️ **Graceful Degradation**: Fallback mechanisms for various scenarios
- 📊 **Detailed Logging**: Comprehensive error reporting and debugging
- 🔄 **Connection Recovery**: Automatic reconnection attempts

### Network Configuration

This add-on uses `host_network: true` which means:
- ✅ Direct access to host network interfaces
- ✅ No need to configure port mappings in add-on settings
- ✅ Optimal performance with minimal network overhead
- ⚠️ Ports must be unique across all services on your host


## Support

### Getting Help

1. **Check the logs** first for error messages
2. **Review this README** for configuration examples
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Your configuration (remove sensitive data)
   - Complete log output
   - Description of the problem

### Reporting Issues

When reporting issues, please include:

```yaml
# Your anonymized configuration
modbus_devices:
  - name: "Device 1"
    host: "192.168.1.XXX"  # Replace with XXX
    port: 502
    bind_port: 5020
# ... rest of config
```

And the complete log output from the add-on.

## Credits

This add-on is based on:
- **Original add-on:** [Akulatraxas/ha-modbusproxy](https://github.com/Akulatraxas/ha-modbusproxy)
- **Modbus Proxy Library:** [tiagocoutinho/modbus-proxy](https://github.com/tiagocoutinho/modbus-proxy)

### Acknowledgments

- **netadair** - Contributed PR with RTU over TCP improvements and RTU issue fixes


## License

See the [LICENSE](LICENSE) file for details.

---
