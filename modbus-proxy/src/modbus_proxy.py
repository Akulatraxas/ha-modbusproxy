#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the modbus-proxy project
#
# Copyright (c) 2020-2021 Tiago Coutinho
# Distributed under the GPLv3 license. See LICENSE for more info.


import asyncio
import pathlib
import argparse
import warnings
import contextlib
import logging.config
import os
import stat
from urllib.parse import urlparse

__version__ = "0.8.2"

# Changelog:
# 0.8.2 - Add RTU(over)TCP, fix RTU issues
# 0.8.1 - Improved RTU support with asyncio serial
#         - Improved RTU/Serial support with pyserial-asyncio
#         - Enhanced IP tracking and request counting
#         - Better device permission handling and udev integration
#         - Improved error handling and connection management
# 0.8.0 - Original version from tiagocoutinho/modbus-proxy


DEFAULT_LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)8s %(name)s: %(message)s"},
        "detailed": {"format": "%(asctime)s %(levelname)8s [%(name)s] %(message)s"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "detailed"}
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

log = logging.getLogger("modbus-proxy")


def parse_url(url):
    if "://" not in url:
        url = f"tcp://{url}"
    result = urlparse(url)
    if not result.hostname:
        url = result.geturl().replace("://", "://0")
        result = urlparse(url)
    return result


class Connection:
    def __init__(self, name, reader, writer):
        self.name = name
        self.reader = reader
        self.writer = writer
        self.log = log.getChild(name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        await self.close()

    @property
    def opened(self):
        if hasattr(self, 'modbus_type') and self.modbus_type == 'rtu':
            # Check RTU/Serial connection
            if hasattr(self, 'serial_writer'):
                return (
                    self.serial_writer is not None
                    and not self.serial_writer.is_closing()
                    and not self.serial_reader.at_eof()
                )
            elif hasattr(self, 'serial'):
                return self.serial is not None and self.serial.is_open
            return False
        else:
            # Check TCP connection
            return (
                self.writer is not None
                and not self.writer.is_closing()
                and not self.reader.at_eof()
            )

    async def close(self):
        if hasattr(self, 'modbus_type') and self.modbus_type == 'rtu':
            # Close RTU/Serial connection
            if hasattr(self, 'serial_writer'):
                self.log.info("closing RTU connection...")
                try:
                    self.serial_writer.close()
                    await self.serial_writer.wait_closed()
                except Exception as error:
                    self.log.info("failed to close RTU: %r", error)
                else:
                    self.log.info("RTU connection closed")
                finally:
                    self.serial_reader = None
                    self.serial_writer = None
            elif hasattr(self, 'serial'):
                self.log.info("closing RTU connection...")
                try:
                    self.serial.close()
                except Exception as error:
                    self.log.info("failed to close RTU: %r", error)
                else:
                    self.log.info("RTU connection closed")
                finally:
                    self.serial = None
        elif self.writer is not None:
            # Close TCP connection
            self.log.info("closing connection...")
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as error:
                self.log.info("failed to close: %r", error)
            else:
                self.log.info("connection closed")
            finally:
                self.reader = None
                self.writer = None

    async def _write(self, data):
        if hasattr(self, 'modbus_type') and self.modbus_type == 'rtu':
            # RTU/Serial write
            if hasattr(self, 'serial_writer'):
                # Async serial
                self.log.debug(f"[RTU:{self.device}] → Request: %d bytes", len(data))
                self.serial_writer.write(data)
                await self.serial_writer.drain()
            elif hasattr(self, 'serial'):
                # Sync serial fallback
                self.log.debug(f"[RTU:{self.device}] → Request: %d bytes", len(data))
                self.serial.write(data)
                self.serial.flush()
        else:
            # TCP write
            self.log.debug(f"[TCP:{self.modbus_host}:{self.modbus_port}] → Request: %d bytes", len(data))
            self.writer.write(data)
            await self.writer.drain()

    async def write(self, data):
        try:
            await self._write(data)
        except Exception as error:
            self.log.error("writting error: %r", error)
            await self.close()
            return False
        return True

    async def _read(self):
        """Read ModBus TCP message from server ie response"""
        # Handle Modbus TCP, RTU and ASCII
        if hasattr(self, 'modbus_type') and ( self.modbus_type == 'rtu' or self.modbus_type == 'rtutcp'):
            # RTU/Serial Modbus - different protocol
            return await self._read_rtu()
        else:
            # TCP Modbus
            header = await self.reader.readexactly(6)
            size = int.from_bytes(header[4:], "big")
            reply = header + await self.reader.readexactly(size)
            
            self.log.debug(f"[TCP:{self.modbus_host}:{self.modbus_port}] ← Response: %d bytes", len(reply))
            
            # Enhanced debug logging for modbus data
            if self.log.isEnabledFor(logging.DEBUG) and len(reply) >= 7:
                self._log_modbus_message(reply, "received")
            
            return reply
    
    async def _read_rtu(self):
        """Read ModBus RTU message from server ie response"""
        # RTU protocol: [slave_id][function_code][data][crc_low][crc_high]
        # We need to read byte by byte to detect frame boundaries
        import struct
        
        # Use appropriate reader based on connection type
        reader = self.serial_reader if hasattr(self, 'serial_reader') else self.reader
        
        # Read first byte (slave ID)
        slave_id = await reader.readexactly(1)
        
        # Read function code
        function_code = await reader.readexactly(1)
        
        # Read data based on function code
        data = b''
        if function_code[0] in [0x01, 0x02, 0x03, 0x04]:  # Read functions
            # Read byte count, then (address (2 bytes) + value (2 bytes)) times byte count/4 
            byte_count = await reader.readexactly(1)
            data = byte_count + await reader.readexactly(byte_count[0])
        elif function_code[0] in [0x05, 0x06, 0x0F, 0x10]:  # Write single, Write multiple
            # Read address (2 bytes) + value (2 bytes)
            data = await reader.readexactly(4)
        
        # Read CRC (2 bytes)
        crc = await reader.readexactly(2)
        
        # Combine into RTU frame
        rtu_frame = slave_id + function_code + data + crc

        if hasattr(self, 'modbus_type') and self.modbus_type == 'rtu':
            self.log.debug(f"[RTU:{self.device}] ← Response: %d bytes", len(rtu_frame))
        else:
            self.log.debug(f"[RTUoverTCP:{self.modbus_host}:{self.modbus_port}] ← Response: %d bytes", len(rtu_frame))
        
        # Enhanced debug logging for RTU data
        if self.log.isEnabledFor(logging.DEBUG) and len(rtu_frame) >= 4:
            self._log_rtu_message(rtu_frame, "received")
        
        return rtu_frame

    async def read(self):
        try:
            return await self._read()
        except asyncio.IncompleteReadError as error:
            if error.partial:
                self.log.error("reading error: %r", error)
            else:
                self.log.info("client closed connection")
            await self.close()
        except Exception as error:
            self.log.error("reading error: %r", error)
            await self.close()

    def _log_modbus_message(self, data, direction):
        """Enhanced logging for modbus messages with parsed details"""
        if len(data) < 7:
            return
            
        try:
            import struct
            # Parse MBAP header
            transaction_id, protocol_id, length, unit_id = struct.unpack('>HHHB', data[:7])
            
            if len(data) > 7:
                function_code = data[7]
                pdu = data[8:]
                
                # Log basic info
                self.log.debug(f"{direction}: TxID={transaction_id}, Unit={unit_id}, FC={function_code:02X}")
                
                # Parse function-specific data for read responses
                if direction == "received" and function_code in [0x01, 0x02, 0x03, 0x04] and len(pdu) > 0:
                    byte_count = pdu[0]
                    if len(pdu) >= 1 + byte_count:
                        values_data = pdu[1:1+byte_count]
                        
                        if function_code in [0x01, 0x02]:  # Coils/Discrete Inputs
                            values = []
                            for i, byte_val in enumerate(values_data):
                                for bit in range(8):
                                    if i * 8 + bit < byte_count * 8:
                                        values.append((byte_val >> bit) & 1)
                            self.log.debug(f"Values: {values[:16]}{'...' if len(values) > 16 else ''}")
                            
                        elif function_code in [0x03, 0x04]:  # Holding/Input Registers
                            values = []
                            for i in range(0, len(values_data), 2):
                                if i + 1 < len(values_data):
                                    value = struct.unpack('>H', values_data[i:i+2])[0]
                                    values.append(value)
                            self.log.debug(f"Registers: {values[:8]}{'...' if len(values) > 8 else ''}")
                            
        except Exception as e:
            self.log.debug(f"Failed to parse modbus message: {e}")

    def _log_rtu_message(self, data, direction):
        """Enhanced logging for RTU modbus messages with parsed details"""
        if len(data) < 4:
            return
            
        try:
            import struct
            # Parse RTU frame: [slave_id][function_code][data][crc_low][crc_high]
            slave_id = data[0]
            function_code = data[1]
            rtu_data = data[2:-2]  # Exclude CRC
            crc = data[-2:]
            
            # Log basic info
            self.log.debug(f"{direction} RTU: Slave={slave_id}, FC={function_code:02X}")
            
            # Parse function-specific data for read responses
            if direction == "received" and function_code in [0x01, 0x02, 0x03, 0x04] and len(rtu_data) > 1:
                byte_count = rtu_data[0]
                if len(rtu_data) >= 1 + byte_count:
                    values_data = rtu_data[1:1+byte_count]
                    
                    if function_code in [0x01, 0x02]:  # Coils/Discrete Inputs
                        values = []
                        for i, byte_val in enumerate(values_data):
                            for bit in range(8):
                                if i * 8 + bit < byte_count * 8:
                                    values.append((byte_val >> bit) & 1)
                        self.log.debug(f"RTU Values: {values[:16]}{'...' if len(values) > 16 else ''}")
                        
                    elif function_code in [0x03, 0x04]:  # Holding/Input Registers
                        values = []
                        for i in range(0, len(values_data), 2):
                            if i + 1 < len(values_data):
                                value = struct.unpack('>H', values_data[i:i+2])[0]
                                values.append(value)
                        self.log.debug(f"RTU Values: {values[:8]}{'...' if len(values) > 8 else ''}")

            # Parse function-specific data for read responses
            if direction == "received_from_client" and function_code in [0x01, 0x02, 0x03, 0x04] and len(rtu_data) >= 4:
                values = []
                for i in range(0, len(rtu_data)-1, 2):
                    value = struct.unpack('>H', rtu_data[i:i+2])[0]
                    values.append(value)
                self.log.debug(f"RTU Registers: {values[:8]}{'...' if len(values) > 8 else ''}")
                        
        except Exception as e:
            self.log.debug(f"Failed to parse RTU message: {e}")


class Client(Connection):
    def __init__(self, reader, writer):
        peer = writer.get_extra_info("peername")
        super().__init__(f"Client({peer[0]}:{peer[1]})", reader, writer)
        self.client_ip = peer[0]
        self.client_port = peer[1]
        self.request_count = 0
        self.log.info(f"new client connection from {self.client_ip}:{self.client_port} -> to Proxy")
        
    async def _write(self, data):
        # Enhanced logging for client writes (responses)
        self.log.debug(f"[{self.client_ip}:{self.client_port}] → Response: %d bytes", len(data))
        if self.log.isEnabledFor(logging.DEBUG):
            if hasattr(self, 'modbus_type') and self.modbus_type == 'tcp':		
                if len(data) >= 7:		
                    self._log_modbus_message(data, "sent_to_client")
                elif len(data) >= 4:
                    self._log_rtu_message(data, "sent_to_client")
        self.writer.write(data)
        await self.writer.drain()
        
    async def _read(self):
        """Read ModBus TCP or RTUoverTCP message from client"""
		
        if hasattr(self, 'modbus_type') and self.modbus_type == 'tcp':
		
            header = await self.reader.readexactly(6)
            size = int.from_bytes(header[4:], "big")
            reply = header + await self.reader.readexactly(size)
            
            self.request_count += 1
            self.log.debug(f"[{self.client_ip}:{self.client_port}] ← Request #{self.request_count}: %d bytes", len(reply))
            
            # Enhanced debug logging for client requests
            if self.log.isEnabledFor(logging.DEBUG) and len(reply) >= 7:
                self._log_modbus_message(reply, "received_from_client")
            
            return reply

        else:
            # Use appropriate reader based on connection type
            reader = self.serial_reader if hasattr(self, 'serial_reader') else self.reader
            
            # Read first byte (slave ID)
            slave_id = await reader.readexactly(1)
            
            # Read function code
            function_code = await reader.readexactly(1)
            
            # Read data based on function code
            data = b''
            if function_code[0] in [0x01, 0x02, 0x03, 0x04]:  # Read functions
                # Read address (2 bytes) + count (2 bytes)
                data = await reader.readexactly(4)
            elif function_code[0] in [0x05, 0x06]:  # Write single
                # Read address (2 bytes) + value (2 bytes)
                data = await reader.readexactly(4)
            elif function_code[0] in [0x0F, 0x10]:  # Write multiple
                # Read address (2 bytes) + count (2 bytes) + byte_count + data
                addr_count = await reader.readexactly(4)
                byte_count = await reader.readexactly(1)
                data = addr_count + byte_count + await reader.readexactly(byte_count[0])
            
            # Read CRC (2 bytes)
            crc = await reader.readexactly(2)
            
            # Combine into RTU frame
            reply = slave_id + function_code + data + crc
   	   	
            self.request_count += 1
            self.log.debug(f"[{self.client_ip}:{self.client_port}] ← Request #{self.request_count}: %d bytes", len(reply))
            
            # Enhanced debug logging for client requests
            if self.log.isEnabledFor(logging.DEBUG) and len(reply) >= 4:
                self._log_rtu_message(reply, "received_from_client")
            
            return reply
				

class ModBus(Connection):
    def __init__(self, config):
        modbus = config["modbus"]
        url = parse_url(modbus["url"])
        bind = parse_url(config["listen"]["bind"])
        
        # Determine if it's RTU or TCP based on URL scheme
        if url.scheme == "rtu":
            self.modbus_type = "rtu"
            device_name = url.path.lstrip('/')  # Remove leading slash
            super().__init__(f"ModBus(RTU:{device_name})", None, None)
            self.device = device_name
            self.baudrate = modbus.get("baudrate", 9600)
            self.databits = modbus.get("databits", 8)
            self.stopbits = modbus.get("stopbits", 1)
            self.parity = modbus.get("parity", "N")
        elif url.scheme == "rtutcp":
            self.modbus_type = "rtutcp"
            super().__init__(f"ModBus({url.hostname}:{url.port})", None, None)
            self.modbus_host = url.hostname
            self.modbus_port = url.port
        else:
            self.modbus_type = "tcp"
            super().__init__(f"ModBus({url.hostname}:{url.port})", None, None)
            self.modbus_host = url.hostname
            self.modbus_port = url.port
        
        self.host = bind.hostname
        self.port = 502 if bind.port is None else bind.port
        self.timeout = modbus.get("timeout", None)
        self.connection_time = modbus.get("connection_time", 0)
        self.unit_id_remapping = config.get("unit_id_remapping") or {}
        self.server = None
        self.lock = asyncio.Lock()

    @property
    def address(self):
        if self.server is not None:
            return self.server.sockets[0].getsockname()

    async def open(self):
        if self.modbus_type == "rtu":
            self.log.info(f"connecting to RTU device {self.device}...")
            
            # Check device permissions and existence
            if not os.path.exists(self.device):
                raise FileNotFoundError(f"Serial device {self.device} not found")
            
            # Check device existence and type
            if not os.path.exists(self.device):
                raise FileNotFoundError(f"Serial device {self.device} not found")
            
            try:
                device_stat = os.stat(self.device)
                if not stat.S_ISCHR(device_stat.st_mode):
                    raise ValueError(f"{self.device} is not a character device")
                
                # Check if we have read/write permissions (set by Supervisor)
                if not os.access(self.device, os.R_OK | os.W_OK):
                    self.log.error(f"Insufficient permissions for {self.device}. Check Supervisor device mapping.")
                    raise PermissionError(f"Cannot access {self.device} - check config.yaml devices list")
            except Exception as e:
                self.log.error(f"Device check failed: {e}")
                raise
            
            # Use asyncio serial connection
            try:
                import serial_asyncio
                self.serial_reader, self.serial_writer = await serial_asyncio.open_serial_connection(
                    url=self.device,
                    baudrate=self.baudrate,
                    bytesize=self.databits,
                    parity=self.parity,
                    stopbits=self.stopbits,
                    timeout=self.timeout
                )
                self.log.info(f"connected to RTU device {self.device}!")
            except ImportError:
                # Fallback to synchronous serial if asyncio version not available
                self.log.warning("pyserial-asyncio not available, using synchronous fallback")
                import serial
                self.serial = serial.Serial(
                    port=self.device,
                    baudrate=self.baudrate,
                    bytesize=self.databits,
                    parity=self.parity,
                    stopbits=self.stopbits,
                    timeout=self.timeout
                )
                self.log.info(f"connected to RTU device {self.device} (sync mode)!")
        else:
            self.log.info(f"connecting Proxy to Modbus Device({self.modbus_host}:{self.modbus_port})...")
            self.reader, self.writer = await asyncio.open_connection(
                self.modbus_host, self.modbus_port
            )
            self.log.info(f"connected to Device({self.modbus_host}:{self.modbus_port})!")

    async def connect(self):
        if not self.opened:
            await asyncio.wait_for(self.open(), self.timeout)
            if self.connection_time > 0:
                self.log.info("delay after connect: %s", self.connection_time)
                await asyncio.sleep(self.connection_time)

    async def write_read(self, data, attempts=2):
        async with self.lock:
            for i in range(attempts):
                try:
                    await self.connect()
                    coro = self._write_read(data)
                    return await asyncio.wait_for(coro, self.timeout)
                except Exception as error:
                    self.log.error(
                        "write_read error [%s/%s]: %r", i + 1, attempts, error
                    )
                    await self.close()

    async def _write_read(self, data):
        await self._write(data)
        return await self._read()

		
    def _crc(self,data):
        crc = 0xffff
        for n in range(len(data)):
            crc ^= data[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc				
		
    def _transform_request(self, request):
	
        if( self.modbus_type == "rtutcp" or self.modbus_type == "rtu"):
	
            uid = request[0]
            new_uid = self.unit_id_remapping.setdefault(uid, uid)
            if uid != new_uid:
                request = bytearray(request)
                request[0] = new_uid

                request = request[0:-2] + self._crc(request[0:-2]).to_bytes(2, byteorder='little')
				
                self.log.debug("remapping unit ID %s to %s in request", uid, new_uid)
            return request
	
	
        else:	
            uid = request[6]
            new_uid = self.unit_id_remapping.setdefault(uid, uid)
            if uid != new_uid:
                request = bytearray(request)
                request[6] = new_uid
                self.log.debug("remapping unit ID %s to %s in request", uid, new_uid)
            return request

    def _transform_reply(self, reply):
	
        if( self.modbus_type == "rtutcp" or self.modbus_type == "rtu"):
	
            uid = reply[0]
            inverse_unit_id_map = {v: k for k, v in self.unit_id_remapping.items()}
            new_uid = inverse_unit_id_map.setdefault(uid, uid)
            if uid != new_uid:
                reply = bytearray(reply)
                reply[0] = new_uid
				
                reply = reply[0:-2] + self._crc(reply[0:-2]).to_bytes(2, byteorder='little')
				
                self.log.debug("remapping unit ID %s to %s in reply", uid, new_uid)
            return reply
	
        else:		
            uid = reply[6]
            inverse_unit_id_map = {v: k for k, v in self.unit_id_remapping.items()}
            new_uid = inverse_unit_id_map.setdefault(uid, uid)
            if uid != new_uid:
                reply = bytearray(reply)
                reply[6] = new_uid
                self.log.debug("remapping unit ID %s to %s in reply", uid, new_uid)
            return reply

    async def handle_client(self, reader, writer):
	
	
        async with Client(reader, writer) as client:
            while True:
                request = await client.read()
                if not request:
                    break
                
                # Log proxy activity overview
                if hasattr(self, 'modbus_type') and self.modbus_type == 'rtu':
                    self.log.debug(f"PROXY: {client.client_ip}:{client.client_port} → RTU:{self.device} (Request #{client.request_count})")
                elif hasattr(self, 'modbus_type') and self.modbus_type == 'rtutcp':
                    self.log.debug(f"PROXY: {client.client_ip}:{client.client_port} → RTU(over)TCP:{self.modbus_host}:{self.modbus_port} (Request #{client.request_count})")
                else:
                    self.log.debug(f"PROXY: {client.client_ip}:{client.client_port} → TCP:{self.modbus_host}:{self.modbus_port} (Request #{client.request_count})")
                
                reply = await self.write_read(self._transform_request(request))
                if not reply:
                    break
                result = await client.write(self._transform_reply(reply))
                if not result:
                    break

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port, start_serving=True
        )

    async def stop(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
        await self.close()

    async def serve_forever(self):
        if self.server is None:
            await self.start()
        async with self.server:
            device_info = f"Device({self.modbus_host}:{self.modbus_port})" if self.modbus_type == "tcp" or self.modbus_type == "rtutcp" else f"Device({self.device})"
            self.log.info(f"Ready to accept requests on {self.host}:{self.port} for {device_info}")
            await self.server.serve_forever()


def load_config(file_name):
    file_name = pathlib.Path(file_name)
    ext = file_name.suffix
    if ext.endswith("toml"):
        from toml import load
    elif ext.endswith("yml") or ext.endswith("yaml"):
        import yaml

        def load(fobj):
            return yaml.load(fobj, Loader=yaml.Loader)

    elif ext.endswith("json"):
        from json import load
    else:
        raise NotImplementedError
    with open(file_name) as fobj:
        return load(fobj)


def prepare_log(config):
    cfg = config.get("logging")
    if not cfg:
        cfg = DEFAULT_LOG_CONFIG
    if cfg:
        cfg.setdefault("version", 1)
        cfg.setdefault("disable_existing_loggers", False)
        logging.config.dictConfig(cfg)
        
        # Note: Using standard Python logging levels (DEBUG, INFO, WARNING, ERROR)
    
    warnings.simplefilter("always", DeprecationWarning)
    logging.captureWarnings(True)
    return log


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="ModBus proxy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c", "--config-file", default=None, type=str, help="config file"
    )
    parser.add_argument("-b", "--bind", default=None, type=str, help="listen address")
    parser.add_argument(
        "--modbus",
        default=None,
        type=str,
        help="modbus device address (ex: tcp://plc.acme.org:502)",
    )
    parser.add_argument(
        "--modbus-connection-time",
        type=float,
        default=0,
        help="delay after establishing connection with modbus before first request",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="modbus connection and request timeout in seconds",
    )
    options = parser.parse_args(args=args)

    if not options.config_file and not options.modbus:
        parser.exit(1, "must give a config-file or/and a --modbus")
    return options


def create_config(args):
    if args.config_file is None:
        assert args.modbus
    config = load_config(args.config_file) if args.config_file else {}
    prepare_log(config)
    log.info("Starting...")
    devices = config.setdefault("devices", [])
    if args.modbus:
        listen = {"bind": ":502" if args.bind is None else args.bind}
        devices.append(
            {
                "modbus": {
                    "url": args.modbus,
                    "timeout": args.timeout,
                    "connection_time": args.modbus_connection_time,
                },
                "listen": listen,
            }
        )
    return config


def create_bridges(config):
    return [ModBus(cfg) for cfg in config["devices"]]


async def start_bridges(bridges):
    coros = [bridge.start() for bridge in bridges]
    await asyncio.gather(*coros)


async def run_bridges(bridges, ready=None):
    async with contextlib.AsyncExitStack() as stack:
        coros = [stack.enter_async_context(bridge) for bridge in bridges]
        await asyncio.gather(*coros)
        await start_bridges(bridges)
        if ready is not None:
            ready.set(bridges)
        coros = [bridge.serve_forever() for bridge in bridges]
        await asyncio.gather(*coros)


async def run(args=None, ready=None):
    args = parse_args(args)
    config = create_config(args)
    bridges = create_bridges(config)
    await run_bridges(bridges, ready=ready)


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.warning("Ctrl-C pressed. Bailing out!")


if __name__ == "__main__":
    main()
