"""Jablotron Sensor platform

HA forum    : https://community.home-assistant.io/t/jablotron-ja-80-series-and-ja-100-series-alarm-integration/113315/

The original code by mattsaxton was for a Jablotron 80 Series System
Github repo: https://github.com/mattsaxon/HASS-Jablotron80

The modified code by plaksnor was for a Jablotron 101 Series 
Github repo: https://github.com/plaksnor/HASS-JablotronSystem

The code from Horsi70 is a fork from plaksnor and for a Jablotron 106 Series but tries to not change the behavior for 101 Series
by just adding parts for the 106 Series
Github repo: https://github.com/Horsi70/HASS-JablotronSystem

The main differences between 101 and 106 series explained

                                JA-101  JA-106
max peripheral devices      =    50       120
max users                   =    50       300
max sections/areas/zones    =     8        15
max programmable outputs PG =    16        32

The packets sent from an 106 Series are longer than the 101 or 80 Series
The codes and commands are different too. This explains why a lot of people have problems with the code from plaksnor 
on their 106

This code is tested on JA-106K-LAN with 92 active devices 

----------------JA-106 Series Description by Horsi70----------------------------------------------------------------------------------------

The packets starting with d8 0d seem to contain some kind of status report.
These packets contain on/off data for 1 or more sensors
They seem to be generated once every minute (line 1,4 example), or eventually but not always at the moment an event is triggered (line 2,3,5 examples)

Four examples:
line  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16   17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32   33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48   49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 <====================== byte number
1    d8 0d 00 00 00 00 00 00 00 00 04 00 00 00 00 00   00 00 00 00 b0 2a 00 10 00 00 00 00 00 00 00 00   68 2a 00 10 89 d3 00 00 00 00 00 00 70 04 00 10   0b 00 00 00 f4 44 00 10 00 00 00 00 ed 58 03 00
2    d8 0d 00 00 00 00 00 00 10 00 04 00 00 00 00 55   08 00 18 01 0b 40 9d f4 15 00 00 00 00 00 00 00   68 2a 00 10 89 d3 00 00 00 00 00 00 70 04 00 10   0b 00 00 00 f4 44 00 10 00 00 00 00 ed 58 03 00
3    d8 0d 00 00 00 00 80 00 10 00 04 00 00 00 00 55   08 81 e4 c0 07 d0 11 d5 17 00 00 00 00 00 00 00   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   4d 39 05 00 0f 3e 01 00 3c 3a 01 00 00 62 00 01
4    d8 0d 00 08 00 00 00 00 10 00 04 00 00 00 00 00   00 00 00 00 b0 2a 00 10 00 00 00 00 00 00 00 00   68 2a 00 10 89 d3 00 00 00 00 00 00 70 04 00 10   0b 00 00 00 f4 44 00 10 00 00 00 00 ed 58 03 00
5    d8 0d 00 00 00 00 00 00 00 00 04 02 00 00 00 55   08 01 6c 41 10 30 97 56 9d 00 00 00 00 00 00 00   68 2a 00 10 89 d3 00 00 00 00 00 00 70 04 00 10   0b 00 00 00 f4 44 00 10 00 00 00 00 ed 58 03 00
6    d8 0d 00 00 00 00 00 00 00 00 00 00 00 00 00 55   08 01 52 81 0e d0 4d 37 1e 00 00 00 00 00 00 00   68 2a 00 10 89 d3 00 00 00 00 00 00 70 04 00 10   0b 00 00 00 f4 44 00 10 00 00 00 00 ed 58 03 00


line 1, active ID's 58 -> nothing triggered
line 2, active ID's 44,58 -> ID 44 triggered dec 44 = hex 2c
line 3, active ID's 31,44,58 -> ID 31 triggered dec 31 = hex 1f
line 4, active ID's 3,44,58
line 5, active ID's 58,65 -> ID 65 triggered dec 65 = hex 41
line 6, active ID's none -> ID 58 closed dec 58 = hex 3a
Remark: for the packets containing on byte 16 the 5509 or 5508, only bytes 18 to 25 seem to change. 18 to 25 not yet deciphered
The bytes 26 to 64 do not change on arm/disarm nor on PG-Output changes

The binary representation of the bytes from 3 to 18 is the vector of active contacts
Example: hex code 2a in binary is 0010 1010 read from right to the left means that contact ID 1,3,5 are active

0010 1010
7654 3210

byte   4---------------------4   5---------------------5   6---------------------6   7---------------------7   8---------------------8   9---------------------9
ID	    7  6  5  4  3  2  1  0   15 14 13 12 11 10  9  8   23 22 21 20 19 18 17 16   31 30 29 28 27 26 25 24   39 38 37 36 35 34 33 32   47 46 45 44 43 42 41 40 

byte   10-------------------10   11-------------------11   12-------------------12   13-------------------13   14-------------------14   15-------------------15
ID	   55 54 53 52 51 50 49 48   63 62 61 60 59 58 57 56   71 70 69 68 67 66 65 64   79 78 77 76 75 74 73 72   87 86 85 84 83 82 81 80   95 94 93 92 91 90 89 88   

byte   16-----------------------16   17---------------------------17   18---------------------------18
ID     103 102 101 100 99 98 97 96   111 110 109 108 107 106 105 104   119 118 117 116 115 114 113 112
 
Means for line 4 example:
byte 4 = hex 08, bin 0000 1000, contact ID 3 is active
byte 9 = hex 10, bin 0001 0000, contact ID 44 is active
byte 11 = hex 04, bin 0000 0100, contact ID 58 is active
								  
 byte number:
  4 upto 15 = accumulated sensor ID's of devices which are ON. See hextobin() function for decoding.
              As in my setup, 92 out of 120 possible devices where activated, the position of the 5508 might be dependant of the number of devices activated.
              If all 120 contacts used, the binary representation would need 15 bytes, so from 4 to 18. As only 92 are used, only 12 bytes neede so from 4 to 15.
              That might be the reason that the 5509 packets start on byte 16 in my setup.
 16 and  17 = if 55 09, a specific sensor recently caused this d8 packet. Maybe 55 09 for wired and 55 09 for a wireless sensor (unconfirmed)
         14 = specific on/off status of a sensor which has changed state


----------------JA-101 Series Description by plaksnor----------------------------------------------------------------------------------------

 The code contains 2 classes:
 - DeviceScanner() is scanning for packets with sensor data
 - JablotronSensor() is representing a binary_sensor object in HA

 The Jablotron data (for at least the JA-100 series) consists of two important type of packets which are getting send by the alarm system.

 -----------------------------------------------------------------------------------
 The packets starting with d8 08 seem to contain some kind of status report.
 These packets contain on/off data for 1 or more sensors

 For example:
  1  2  3  4  5  6  7  8   9 10 11 12 13 14 15 16  <====================== byte number
 d8 08 00 00 00 00 00 00  00 00 00 10 14 55 00 10  |.............U..|    : nothing is activated
 d8 08 00 00 01 00 00 00  00 00 55 09 00 88 00 02  |..........U.....|    : one or multiple devices has been activated

 byte number:
  4 and  5 = accumulated sensor ID's of devices which are ON. See hextobin() function for decoding. This data is not being used right now.
------------ the next bytes are not used, but already deciphered
 11 and 12 = if 55 09, a specific sensor recently caused this d8 packet
        14 = specific on/off status of a sensor which has changed state
 15 and 16 = specific sensor ID of sensor which has changed state


 -----------------------------------------------------------------------------------
 The packets starting with 55 09 also seem to contain sensor data, but they are only getting send when there has been send a d8 or 55 packet in the last 30 seconds.
 These packets contain on/off data for only 1 sensor, not multiple

 For example:
  1  2  3  4  5  6  7  8   9 10 11 12 13 14 15 16  <====================== byte number
 55 09 00 8a 00 02 40 cc  d2 3b 13 00 0b 00 00 00  |U.....@..;......|    : sensor 00 02 became inactive (8a)
 55 09 00 80 80 01 60 cc  f2 3b 14 00 14 55 00 10  |U.....`..;...U..|    : sensor 80 01 became active (80)

 byte number:
         4 = status (on/off) of device which has changed state
  5 and  6 = specific sensor ID of sensor which has changed state

 -----------------------------------------------------------------------------------

 Recent discoveries
 55 08 = wired    (unconfirmed)
 55 09 = wireless (unconfirmed)

"""

import logging
import binascii
import sys
import re
import time
import asyncio
import threading
import voluptuous as vol

from . import DOMAIN

from concurrent.futures import ThreadPoolExecutor
from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA,
    BinarySensorDevice,
)
from homeassistant.const import (
    STATE_ON,
    STATE_OFF
)
import homeassistant.components.sensor as sensor
import homeassistant.helpers.config_validation as cv

from homeassistant import util
from homeassistant.config import load_yaml_config_file, async_log_exception
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.util.yaml import dump

_LOGGER = logging.getLogger(__name__)

devices = []
YAML_DEVICES = 'jablotron_devices.yaml'

async def async_setup_platform(hass: HomeAssistantType, config: ConfigType, async_add_entities, discovery_info=None):
    yaml_path = hass.config.path(YAML_DEVICES)
    devices = await async_load_config(yaml_path, hass, config, async_add_entities)
    data = DeviceScanner(hass, config, async_add_entities, devices)


class JablotronSensor(BinarySensorDevice):
    """Representation of a Sensor."""

    def __init__(self, hass: HomeAssistantType, dev_id: str):
        self._hass = hass
        self._name = 'Jablotron sensor'
        self._state = STATE_OFF
        self.dev_id = dev_id
        _LOGGER.debug('JablotronSensor.__init__(): dev_id created: %s', self.dev_id)

    @property
    def name(self):
        """Return the name of the sensor."""
#        return self.name
        return self.dev_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def _update(self):
        """Update state to HA"""
        self.async_schedule_update_ha_state()
        _LOGGER.debug('JablotronSensor._update(): sensor updated')

    async def async_seen(self, state: str = None):
        """Mark the device as seen."""
        if self._state != state:
            self._state = state

            _LOGGER.debug('JablotronSensor.async_seen(): state updated to %s', state)
#            await self._update()
#            await self.async_update()

#    async def async_update(self):
#        """Update state of entity.
#        This method is a coroutine.
#        """
##        self._state = STATE_OFF
#        _LOGGER.info('async_update: updated')










class DeviceScanner():
    """ Read configuration and serial port and check for incoming data"""

    def __init__(self, hass, config, async_add_entities, devices):
        self._state = None
        self._sub_state = None
        self._file_path = hass.data[DOMAIN]['port']
        self._available = False
        self._f = None
        self._hass = hass
        self._config = config
        self._model = 'Unknown'
        self._lock = threading.BoundedSemaphore()
        self._stop = threading.Event()
        self._data_flowing = threading.Event()
        self._async_add_entities = async_add_entities
        self.devices = {dev.dev_id: dev for dev in devices}
        self._is_updating = asyncio.Lock()
        self._activation_packet = b''
        self._mode = '55'

        """ default binary strings for comparing states in d8 packets """
        """ length was fix to 32 for 101 series. Set to 12*8 for 106 series, but should still work for 101 series """
        self._old_bin_string = '0'.zfill(12*8)
        self._new_bin_string = '0'.zfill(12*8)

        _LOGGER.debug('DeviceScanner.__init__(): serial port: %s', format(self._file_path))

        switcher = {
            "0": b'\x30',
            "1": b'\x31',
            "2": b'\x32',
            "3": b'\x33',
            "4": b'\x34',
            "5": b'\x35',
            "6": b'\x36',
            "7": b'\x37',
            "8": b'\x38',
            "9": b'\x39'
        }

        try:

            """ generate activation packet containing the alarm code, to trigger the right sensor packets """
            packet_code = b''
            for c in hass.data[DOMAIN]['code']:
                packet_code = packet_code + switcher.get(c)
#            self._activation_packet = b'\x80\x08\x03\x39\x39\x39' + packet_code
# This breaks compatibility with JA-101 for now
            self._activation_packet = b'\x80\x08\x03\x30' + packet_code

            hass.bus.async_listen('homeassistant_stop', self.shutdown_threads)

            self._io_pool_exc = ThreadPoolExecutor(max_workers=5)
            self._read_loop_future = self._io_pool_exc.submit(self._read_loop)
            self._watcher_loop_keepalive_future = self._io_pool_exc.submit(self._watcher_loop_keepalive)
            self._watcher_loop_triggersensorupdate_future = self._io_pool_exc.submit(self._watcher_loop_triggersensorupdate)
#            self._io_pool_exc.submit(self._keepalive)
#            self._io_pool_exc.submit(self._triggersensorupdate)

        except Exception as ex:
            _LOGGER.error('Unexpected error 1: %s', format(ex) )

    def shutdown_threads(self, event):
        _LOGGER.debug('DeviceScanner.shutdown_threads: handle_shutdown() called' )
        self._stop.set()
        _LOGGER.debug('DeviceScanner.shutdown_threads: exiting handle_shutdown()' )

    @property
    def name(self):
        """Return the name of the DeviceScanner."""
        return 'Jablotron scanner'

    @property
    def state(self):
        """Return the state of the DeviceScanner."""
        return self._state

    @property
    def available(self):
        """Return the availability of incoming data of the DeviceScanner."""
        return self._available


#    async def _update(self):
#            self.async_schedule_update_ha_state()

    def _watcher_loop_keepalive(self):
        """Trigger keepalive message to get d8 08 packets."""
        while not self._stop.is_set():
            if not self._data_flowing.wait(0.5):
                self._keepalive()
            else:
                time.sleep(1)

    def _watcher_loop_triggersensorupdate(self):
        """Trigger authentication message to get 55 09 packets."""
        while not self._stop.is_set():
            if not self._data_flowing.wait(0.5):
                self._triggersensorupdate()
            else:
                time.sleep(15)

    def _read_loop(self):
        """Read incoming data"""
        try:
            while not self._stop.is_set():

                self._f = open(self._file_path, 'rb', 64)
                new_state = self._read()

                self._f.close()
                time.sleep(0.5)

        except Exception as ex:
            _LOGGER.error('DeviceScanner._read_loop(): Unexpected error: %s', format(ex) )

        finally:
            _LOGGER.debug('DeviceScanner._read_loop(): Exiting _read_loop()' )

    # function to transform a hex string into a binary string
    def _hextobin(self, hexstring):
        dec = int.from_bytes(hexstring, byteorder=sys.byteorder) # turn to 'little' if sys.byteorder is wrong
        bin_dec = bin(dec)
        binstring = bin_dec[2:]
        binstring = binstring.zfill(len(hexstring)*8)
        revstring = binstring [::-1]
        return revstring



    async def async_see(self, dev_id: str = None, state: str = None):
        """Create binary sensor.
        This method is a coroutine.
        """

        dev_id = cv.slug(str(dev_id).lower())
        device = self.devices.get(dev_id)

        """State received of already known device"""
        if device:
            await device.async_seen(state)
            await device.async_update_ha_state()
            return

        """State received of unknown device"""
        dev_id = util.ensure_unique_string(dev_id, self.devices.keys())
        device = JablotronSensor(self._hass, dev_id)
        self.devices[dev_id] = device

        await device.async_seen(state)

        """Update known_devices.yaml"""
        self._hass.async_create_task(
            self.async_update_config(
                self._hass.config.path(YAML_DEVICES), dev_id, device)
        )

        self._async_add_entities([device])
        _LOGGER.debug('DeviceScanner.async_see(): added entity %s', device)
        
#        _LOGGER.info("async_see: nu gaan we async_update_ha_state aanroepen")
#        if device.track:
#        await device.async_update_ha_state()


    async def async_update_config(self, path, dev_id, device):
        """Add device to YAML configuration file.
        This method is a coroutine.
        """
        async with self._is_updating:
            await self._hass.async_add_executor_job(
                update_config, self._hass.config.path(YAML_DEVICES),
                dev_id, device)

    def _read(self):
        """Read incoming data on port"""
        try:
            while True:

                """Try to read data"""
                self._data_flowing.clear()
                packet = self._f.read(64)
                self._data_flowing.set()

                if not packet:
                    _LOGGER.warn("PortScanner._read(): No packets")
                    self._available = False
                    return 'No Signal'

                self._state = True

                """If data can be read, scan for specific incoming packets"""
                if packet[:2] == b'\xd8\x08':

                    _LOGGER.debug('PortScanner._read(): d8 08 packet, part 1: %s', str(binascii.hexlify(packet[0:8]), 'utf-8'))
                    _LOGGER.debug('PortScanner._read(): d8 08 packet, part 2: %s', str(binascii.hexlify(packet[8:16]), 'utf-8'))

                    byte3 = packet[2:3]  # 3rd byte unknown, always 00
                    byte4 = packet[3:4]  # 4th byte, last part of id
                    byte5 = packet[4:5]  # 5th byte, first part of id

                    """Decode sensor ID from 4th and 5th byte, create a binary string and compare this with the last generated binary string. 0 = OFF, 1 = ON"""
                    self._new_bin_string = self._hextobin(byte4+byte5)
                    _LOGGER.debug('PortScanner._read(): old_bin_string: %s', self._old_bin_string)
                    _LOGGER.debug('PortScanner._read(): new_bin_string: %s', self._new_bin_string)

                    for idx, (x, y) in enumerate(zip(self._old_bin_string, self._new_bin_string)):
                      
                        """Continue for devices which has been changed to ON or OFF."""
                        if x != y:

                            dev_id = 'jablotron_' + str(idx)
                            entity_id = 'binary_sensor.' + dev_id

                            if y == '1':
                                _device_state = STATE_ON
                            else:
                                _device_state = STATE_OFF

                            """Only create or update a sensor when this packet is the first d8 08 packet received since startup,
                               or if d8 08 packet reports about 1 specific device (by containing a 55 packet) or,
                               or if a specific device is not active anymore (y == '0')"""
#                            if self._available == False or (y == '1' and packet[10:12] == b'\x55\x09') or y == '0':
#                            if self._mode == 'd8' or (self._mode == '55' and (self._available == False or (y == '1' and packet[10:12] == b'\x55\x09') or y == '0')):
                            if self._mode == 'd8' or (self._mode == '55' and (self._available == False or (y == '1' and packet[10:11] == b'\x55') or y == '0')):

                                """ Create or update sensor """
                                self._hass.add_job(
                                    self.async_see(dev_id, _device_state)
                                )

                    """Retain last binary string"""
                    _LOGGER.debug('PortScanner._read(): updating bin string to %s', self._new_bin_string)
                    self._old_bin_string = self._new_bin_string

                    """Set available to True since we know which devices are ON"""
                    self._available = True
		
# This part is for 106 series		
                elif packet[:2] == b'\xd8\x0d':

                    _LOGGER.debug('PortScanner._read(): d8 0d packet, part 1: %s', str(binascii.hexlify(packet[0:16]), 'utf-8'))
                    _LOGGER.debug('PortScanner._read(): d8 0d packet, part 2: %s', str(binascii.hexlify(packet[16:32]), 'utf-8'))
                    _LOGGER.debug('PortScanner._read(): d8 0d packet, part 3: %s', str(binascii.hexlify(packet[32:48]), 'utf-8'))
                    _LOGGER.debug('PortScanner._read(): d8 0d packet, part 4: %s', str(binascii.hexlify(packet[48:64]), 'utf-8'))

                    byte4 = packet[3:4]  # first byte containing binary on/off information for ID's 0 to 7
                    byte5 = packet[4:5]  # next byte containing binary on/off information for ID's 8 to 15
                    byte6 = packet[5:6]  # next byte containing binary on/off information for ID's 16 to 23
                    byte7 = packet[6:7]  # next byte containing binary on/off information for ID's 24 to 31
                    byte8 = packet[7:8]  # next byte containing binary on/off information for ID's 32 to 39
                    byte9 = packet[8:9]  # next byte containing binary on/off information for ID's 40 to 47
                    byte10 = packet[9:10]  # next byte containing binary on/off information for ID's 48 to 55
                    byte11 = packet[10:11]  # next byte containing binary on/off information for ID's 56 to 63
                    byte12 = packet[11:12]  # next byte containing binary on/off information for ID's 64 to 71
                    byte13 = packet[12:13]  # next byte containing binary on/off information for ID's 71 to 79
                    byte14 = packet[13:14]  # next byte containing binary on/off information for ID's 80 to 87
                    byte15 = packet[14:15]  # next byte containing binary on/off information for ID's 88 to 95
			
			
                    """Decode sensor ID from 4th and 15th byte, create a binary string and compare this with the last generated binary string. 0 = OFF, 1 = ON"""
                    self._new_bin_string = self._hextobin(byte4+byte5+byte6+byte7+byte8+byte9+byte10+byte11+byte12+byte13+byte14+byte15)
                    _LOGGER.debug('PortScanner._read(): old_bin_string: %s', self._old_bin_string)
                    _LOGGER.debug('PortScanner._read(): new_bin_string: %s', self._new_bin_string)

                    for idx, (x, y) in enumerate(zip(self._old_bin_string, self._new_bin_string)):
                      
                        """Continue for devices which has been changed to ON or OFF."""
                        if x != y:

                            dev_id = 'jablotron_' + str(idx)
                            entity_id = 'binary_sensor.' + dev_id

                            if y == '1':
                                _device_state = STATE_ON
                            else:
                                _device_state = STATE_OFF

                            """Only create or update a sensor when this packet is the first d8 0d packet received since startup,
                               or if d8 08 packet reports about 1 specific device (by containing a 55 packet) or,
                               or if a specific device is not active anymore (y == '0')"""
#                            if self._available == False or (y == '1' and packet[10:12] == b'\x55\x09') or y == '0':
#                            if self._mode == 'd8' or (self._mode == '55' and (self._available == False or (y == '1' and packet[10:12] == b'\x55\x09') or y == '0')):
                            if self._mode == 'd8' or (self._mode == '55' and (self._available == False or (y == '1' and packet[15:16] == b'\x55') or y == '0')):

                                """ Create or update sensor """
                                self._hass.add_job(
                                    self.async_see(dev_id, _device_state)
                                )

                    """Retain last binary string"""
                    _LOGGER.debug('PortScanner._read(): updating bin string to %s', self._new_bin_string)
                    self._old_bin_string = self._new_bin_string

                    """Set available to True since we know which devices are ON"""
                    self._available = True


                elif self._mode == '55' and packet[:2] in (b'\x55\x08', b'\x55\x09'):

                    _LOGGER.debug('PortScanner._read(): %s packet, part 1: %s', str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(packet[0:8]), 'utf-8'))
                    _LOGGER.debug('PortScanner._read(): %s packet, part 2: %s', str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(packet[8:16]), 'utf-8'))

                    packetpart = packet[0:10]

                    byte3 = packetpart[2:3]  # 3rd byte, state of device
                    byte4 = packetpart[3:4]  # 4th byte, unknown
                    byte5 = packetpart[4:5]  # 5th byte, first part of device ID
                    byte6 = packetpart[5:6]  # 6th byte, second part of device ID

                    """Only process specific state changes"""
                    if byte3 in (b'\x00', b'\x01'):
#                        if byte4 in (b'\x6d', b'\x75', b'\x79', b'\x7d', b'\x88', b'\x80'):
                        # 6d, 75, 79, 7d, 88 and 80 are statusses for wireless sensors
                        # 8c and 84 are ON statusses for wired sensors
                        if byte4 in (b'\x6d', b'\x75', b'\x79', b'\x7d', b'\x80', b'\x84', b'\x88', b'\x8c'):
                            _device_state = STATE_ON
                        else:
                            _device_state = STATE_OFF

                        """Decode sensor ID from 5th and 6th byte"""
                        dec = int.from_bytes(byte5+byte6, byteorder=sys.byteorder) # turn to 'little' if sys.byteorder is wrong
                        i = int(dec/64)

                        dev_id = 'jablotron_' + str(i)
                        entity_id = 'binary_sensor.' + dev_id

                        """ Create or update sensor """
                        self._hass.add_job(
                            self.async_see(dev_id, _device_state)
                        )

                    elif byte3 == b'\x0c':
                        # we don't know yet. Must be some keep alive packet from a sensor who hasn't been triggered in a loooong time
                        _LOGGER.debug("Unrecognized %s 0c packet: %s %s %s %s", str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(byte3), 'utf-8'), str(binascii.hexlify(byte4), 'utf-8'), str(binascii.hexlify(byte5), 'utf-8'), str(binascii.hexlify(byte6), 'utf-8'))
                        _LOGGER.debug("Probably Control Panel OFF?")

                    elif byte3 == b'\x2e':
                        # we don't know yet. Must be some keep alive packet from a sensor who hasn't been triggered in a loooong time
                        _LOGGER.debug("Unrecognized %s 2e packet: %s %s %s %s", str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(byte3), 'utf-8'), str(binascii.hexlify(byte4), 'utf-8'), str(binascii.hexlify(byte5), 'utf-8'), str(binascii.hexlify(byte6), 'utf-8'))
                        _LOGGER.debug("Probably Control Panel ON?")

                    elif byte3 == b'\x4f':
                        # we don't know yet. Must be some keep alive packet from a sensor who hasn't been triggered in a loooong time
                        _LOGGER.debug("Unrecognized %s 4f packet: %s %s %s %s", str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(byte3), 'utf-8'), str(binascii.hexlify(byte4), 'utf-8'), str(binascii.hexlify(byte5), 'utf-8'), str(binascii.hexlify(byte6), 'utf-8'))
                        _LOGGER.debug("Probably some keep alive packet from a sensor which hasn't been triggered recently")

                    else:
                        _LOGGER.debug("New unknown %s packet: %s %s %s %s", str(binascii.hexlify(packet[0:2]), 'utf-8'), str(binascii.hexlify(byte3), 'utf-8'), str(binascii.hexlify(byte4), 'utf-8'), str(binascii.hexlify(byte5), 'utf-8'), str(binascii.hexlify(byte6), 'utf-8'))

                else:
                    pass
#                    _LOGGER.info("Unknown packet: %s", packet)
#                    self._stop.set()

        except (IndexError, FileNotFoundError, IsADirectoryError, UnboundLocalError, OSError):
            _LOGGER.warning("PortScanner._read(): File or data not present at the moment: %s", self._file_path)
            return 'Failed'

        except Exception as ex:
            _LOGGER.error('PortScanner._read(): Unexpected error 3: %s', format(ex) )
            return 'Failed'

        return state

    def _sendPacket(self, packet):
        f = open(self._file_path, 'wb')
        f.write(packet)
        time.sleep(0.1) # lower reliability without this delay
        f.close()

    def _triggersensorupdate(self):
        """ Send trigger for sensor update to system"""

#        _LOGGER.debug('PortScanner._triggersensorupdate(): Send activation packet: %s', self._activation_packet)
        _LOGGER.debug('PortScanner._triggersensorupdate(): Send activation packet: <blurred>')
        _LOGGER.debug('PortScanner._triggersensorupdate(): Send packet: 52 02 13 05 9a')

        self._sendPacket(self._activation_packet)
        self._sendPacket(b'\x52\x02\x13\x05\x9a')

    def _keepalive(self):
        """ Send keepalive to system"""

        _LOGGER.debug('PortScanner._triggersensorupdate(): Send packet 52 01 02')
        self._sendPacket(b'\x52\x01\x02')






async def async_load_config(path: str, hass: HomeAssistantType, config: ConfigType, async_add_entities):
    """Load devices from YAML configuration file.
    This method is a coroutine.
    """
    dev_schema = vol.Schema({
        vol.Required('dev_id'): cv.string,
#        vol.Required(CONF_NAME): cv.string,
#        vol.Optional(CONF_ICON, default=None): vol.Any(None, cv.icon),
#        vol.Optional('track', default=False): cv.boolean,
#        vol.Optional(CONF_MAC, default=None):
#            vol.Any(None, vol.All(cv.string, vol.Upper)),
#        vol.Optional(CONF_AWAY_HIDE, default=DEFAULT_AWAY_HIDE): cv.boolean,
#        vol.Optional('gravatar', default=None): vol.Any(None, cv.string),
#        vol.Optional('picture', default=None): vol.Any(None, cv.string),
#        vol.Optional(CONF_CONSIDER_HOME, default=consider_home): vol.All(
#            cv.time_period, cv.positive_timedelta),
    })
    result = []
    try:
        _LOGGER.debug("async_load_config(): reading config file %s", path)

        devices = await hass.async_add_job(
            load_yaml_config_file, path)

        _LOGGER.debug('async_load_config(): devices loaded from config file: %s', devices)
       
    except HomeAssistantError as err:
        _LOGGER.error("async_load_config(): unable to load %s: %s", path, str(err))
        return []
    except FileNotFoundError as err:
        _LOGGER.debug("async_load_config(): file %s could not be found: %s", path, str(err))
        return []


    for dev_id, device in devices.items():
        # Deprecated option. We just ignore it to avoid breaking change
#        device.pop('vendor', None)
        try:
            device = dev_schema(device)
            device['dev_id'] = cv.slugify(dev_id)
        except vol.Invalid as exp:
            async_log_exception(exp, dev_id, devices, hass)
        else:
            dev = JablotronSensor(hass, **device)
            result.append(dev)

            """ Create sensors for each device in devices """
#            device = JablotronSensor(hass, dev_id)
            async_add_entities([dev])
    return result

def update_config(path: str, dev_id: str, device: JablotronSensor):
    """Add device to YAML configuration file."""

    with open(path, 'a') as out:
        device = {device.dev_id: {
            'dev_id': device.dev_id,
#            ATTR_NAME: device._name,
#            ATTR_MAC: sensor.mac,
#            ATTR_ICON: sensor.icon,
#            'picture': sensor.config_picture,
#            'track': sensor.track,
#            CONF_AWAY_HIDE: sensor.away_hide,
        }}
        out.write('\n')
        out.write(dump(device))
    _LOGGER.debug('update_config(): updated %s with sensor %s', path, dev_id)
