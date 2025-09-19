# Changelog

## [2.2.1-beta] - 2025-09-19

### Added
- **RTU over TCP Support** - Full support for Modbus RTU over TCP connections (`rtutcp://` scheme)
- **Enhanced RTU Protocol Handling** - Improved RTU message parsing and CRC calculation
- **RTU over TCP Unit ID Remapping** - Support for unit ID remapping in RTU over TCP connections

### Fixed
- **RTU Connection Issues** - Fixed RTU serial connection stability and error handling
- **RTU Message Parsing** - Improved RTU frame detection and message boundary handling
- **CRC Calculation** - Fixed CRC calculation for RTU protocol messages
- **RTU Connection Recovery** - Enhanced connection recovery mechanisms for RTU devices

### Enhanced
- **RTU Protocol Support** - Better handling of RTU over TCP vs traditional RTU over serial
- **Message Logging** - Enhanced debug logging for RTU over TCP connections
- **Connection Management** - Improved connection state tracking for RTU protocols

### Technical Improvements
- **modbus_proxy.py v0.8.2** - Updated core proxy implementation with RTU over TCP support
- **Protocol Detection** - Automatic detection of RTU vs RTU over TCP vs TCP protocols
- **Enhanced Error Handling** - Better error handling and recovery for RTU connections
- **CRC Validation** - Proper CRC calculation and validation for RTU messages

### Core Proxy Updates (modbus_proxy.py v0.8.2)
- **RTU over TCP Support** - New `rtutcp://` URL scheme for RTU over TCP connections
- **Enhanced RTU Message Parsing** - Improved RTU frame parsing with proper CRC handling
- **Fixed RTU Issues** - Resolved connection stability and message parsing problems
- **Improved Protocol Handling** - Better distinction between RTU, RTU over TCP, and TCP protocols
- **Enhanced Debug Logging** - Better logging for RTU over TCP connections with protocol identification
- **CRC Calculation Fix** - Proper CRC calculation for RTU protocol messages
- **Connection State Management** - Improved connection state tracking for all protocol types

### Configuration Changes
- Added support for `rtutcp://` URL scheme in modbus device configuration
- Enhanced RTU protocol detection and handling
- Improved unit ID remapping for RTU over TCP connections

### Acknowledgments
- **netadair** - Contributed PR with RTU over TCP improvements and RTU issue fixes

## [2.2.0-beta] - 2025-09-15

### Added
- **RTU/Serial Modbus Support** - Full support for Modbus RTU over serial connections
- **RTU over TCP Support** - Support for Modbus RTU over TCP connections
- **Simplified Unit ID Remapping** - New simple syntax `1<>10,2<>20` instead of JSON
- **Auto-Detection** - Plug & play serial device detection with priority-based device selection
- **Enhanced INFO Messages** - Clear Client ↔ Proxy ↔ Device tracking with improved connection status
- **Request Counting** - Track number of requests per client connection
- **Protocol Field** - Explicit protocol specification (`tcp` or `rtu`)
- **Asyncio Serial Support** - Non-blocking serial communication using `pyserial-asyncio`
- **Udev Integration** - Automatic device permissions and hot-plug support
- **Enhanced IP Tracking** - Detailed client IP monitoring and request tracking
- **Device Permission Management** - Automatic permission handling and validation

### Enhanced
- **Serial Communication** - Improved RTU/Serial support with fallback mechanisms
- **Error Handling** - Comprehensive device validation and graceful degradation
- **Logging System** - Simplified logging with standard Python levels and improved INFO messages
- **Device Management** - Better serial device detection and configuration
- **Connection Management** - Improved connection recovery and stability

### Technical Improvements
- **modbus_proxy.py v0.8.1** - Updated core proxy implementation with enhanced features
- **Dockerfile** - Added `pyserial-asyncio` and system packages for serial support
- **Udev Rules** - Automatic permission setting for USB-Serial adapters
- **Auto-Detection Priority** - Stable device identifiers, USB adapters, ACM devices
- **Permission Validation** - Comprehensive device existence and permission checks

### Core Proxy Updates (modbus_proxy.py v0.8.1)
- **Simplified Logging** - Standard Python logging levels (DEBUG, INFO, WARNING, ERROR)
- **Enhanced INFO Messages** - Clear Client ↔ Proxy ↔ Device tracking with improved connection status
- **Asyncio Serial Support** - Non-blocking serial I/O with fallback to synchronous
- **Enhanced IP Tracking** - Client IP and port tracking in all log messages
- **Request Counting** - Per-client request counter for activity monitoring
- **Device Permission Checks** - Comprehensive device validation and permission handling
- **Improved Error Handling** - Better exception handling and connection recovery
- **RTU Message Parsing** - Enhanced RTU protocol message parsing and logging

### Configuration Changes
- Added `auto_detect_device` option (default: `true`)
- Added `protocol` field for explicit protocol specification
- Extended RTU parameters: `device`, `baudrate`, `databits`, `stopbits`, `parity`
- Updated logging levels: `debug`, `info`, `warning`, `error`
- **Simplified Unit ID Remapping Syntax** - New format: `"1<>10,2<>20"` (backward compatible with JSON)

### Breaking Changes
- **None** - This version is fully backward compatible with 2.1.0
- **Unit ID Remapping Syntax** - New simplified syntax recommended, but JSON format still supported

### Known Issues
- Serial device auto-detection requires `privileged: true` mode
- Some USB-Serial adapters may need manual permission configuration
- RTU communication performance depends on device response times

## [2.1.0] - 2024-08-27

### Added
- **Unit ID Remapping Support** - Map incoming unit IDs to target unit IDs on Modbus servers
- Enhanced configuration examples with unit ID remapping
- Improved error handling and validation

## [2.0.0] - Previous Release

⚠️ **BREAKING CHANGES WARNING** ⚠️

**IMPORTANT:** Version 2.0.0+ introduces a completely new configuration format that is **NOT compatible** with version 1.0.0 configurations.

**Before upgrading from 1.0.0:**
1. **Document your current settings** - Write down all your modbus device configurations from version 1.0.0
2. **Read the new README** - Check the updated configuration examples and parameter documentation  
3. **Reconfigure after upgrade** - You will need to completely reconfigure your modbus devices using the new format

**What changed:**
- Configuration parameter names and structure have changed
- New dynamic device support with different syntax
- Enhanced validation and error handling

### Added
- Dynamic number of modbus devices support (unlimited devices)
- Multi-device configuration through Home Assistant UI
- Configurable timeouts and connection parameters
- New configuration validation system

## [1.0.0] - Initial Release

### Added
- Initial fork version with three modbus host configurations
- Basic proxy functionality for single modbus connections
- Home Assistant addon integration


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
