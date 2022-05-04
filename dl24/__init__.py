import binascii
import datetime
import logging
import math
import struct
import time
from dataclasses import dataclass
from typing import Optional

import serial

from dl24.crc import calc_crc_for_payload

logger = logging.getLogger("dl24.serial")

IS_ON = 0x10
VOLTAGE = 0x11
CURRENT = 0x12
TIME = 0x13
CAP_AH = 0x14
CAP_WH = 0x15
TEMP = 0x16
LIM_CURR = 0x17
LIM_VOLT = 0x18
TIMER = 0x19

OUTPUT = 0x01
SETCURR = 0x02
SETVCUT = 0x03
SETTMR = 0x04
RESET_COUNTERS = 0x05

ByteWaitTime_s = 4
PacketWaitTime_s = 4


def unpack_uint24(data):
    return struct.unpack(">I", b'\x00' + data)[0]


def unpack_uint16(data):
    return struct.unpack(">H", data[1:])[0]


@dataclass
class ValueReplyPacket:
    data: bytes


@dataclass
class AckReply:
    pass


@dataclass
class BroadcastPacket:
    voltage: float  # V
    current: float  # A
    capacity: float  # mAh
    energy: int
    temperature: int  # celsius
    time: datetime.timedelta

    @property
    def power(self):
        return self.voltage * self.current


def _parse_broadcast(data: bytes) -> BroadcastPacket:
    #  0                        1                     2                         3
    #  0 1  2  3  4 5 6  7 8 9  0 1 2  3 4 5 6  7 8 9 0 1 2 3 4  5  6  7  8  9  0 1 2 3 4  5
    # ff55|01|02|000047|0001f2|00002c|00000000|0000000000000000|1b|00|00|15|25|3c00000000|43
    # HDR  TP CMD   VOL   CURR    CAP   ENERGY                 TEMP   HH MM SS            CRC
    # ff55 01 02 000073 002ee3 00240e 0000006f 0000000000000000 2d 00 07 2c 1c 3c00000000 a4

    def get_int(format_: str, pos: int):
        pos = pos - 2
        b = data[pos:pos + struct.calcsize(format_)]
        return struct.unpack(format_, b)[0]

    return BroadcastPacket(
            voltage=get_int("B", 6) / 10,
            current=get_int(">H", 8) / 1000,
            capacity=get_int(">H", 11) * 10 / 1000,
            energy=get_int(">H", 15) * 10,
            temperature=get_int("B", 25),
            time=datetime.timedelta(
                    hours=get_int("B", 27),
                    minutes=get_int("B", 28),
                    seconds=get_int("B", 29)),
    )


class DL24Error(Exception):
    pass


class DL24:
    def __init__(self, port: str):
        self.serial = serial.Serial(port=port, timeout=ByteWaitTime_s,
                                    baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    def close(self):
        self.serial.close()

    def _serial_read(self, length: int):
        data = self.serial.read(length)
        if data is None:
            logger.debug("[read] <none>")
        else:
            logger.debug("[read] " + binascii.hexlify(data, " ").decode("ascii"))
        return data

    def _serial_write(self, data: bytes):
        logger.debug("[write] " + binascii.hexlify(data, " ").decode("ascii"))
        self.serial.write(data)

    def _read_packet(self):
        packet_type = self._serial_read(1)
        if packet_type == b'\xca':
            d = self._serial_read(1)
            if len(d) == 0:
                return None
            return self._read_value_resp()
        elif packet_type == b'\xff':
            d = self._serial_read(1)
            if len(d) == 0:
                return None
            return self._read_broadcast()
        elif packet_type == b'\x6f':
            return AckReply()
        else:
            self._serial_read(self.serial.in_waiting)
            return None

    def _read_broadcast(self) -> Optional[BroadcastPacket]:
        resp = self._serial_read(36 - 2)
        if len(resp) != 34:
            return None

        crc = calc_crc_for_payload(resp[:-1])
        if crc != resp[-1]:
            return None

        return _parse_broadcast(resp)

    def _read_value_resp(self) -> ValueReplyPacket:
        resp = self._serial_read(7 - 2)

        if resp[-2:] != b'\xce\xcf':
            raise DL24Error("invalid resp")

        return ValueReplyPacket(data=resp[:-2])

    def _wait_for_packet(self, packet_type):
        p = self._read_packet()

        s = time.time()
        while not isinstance(p, packet_type) or p is None:
            p = self._read_packet()
            if time.time() - s > PacketWaitTime_s:
                raise DL24Error("no response")

        if not isinstance(p, packet_type):
            raise DL24Error("invalid packet")
        return p

    def wait_for_broadcast(self):
        return self._wait_for_packet(BroadcastPacket)

    def read_value(self, payload):
        frame = bytearray([0xb1, 0xb2, *payload, 0xb6])
        self._serial_write(frame)

        p = self._wait_for_packet(ValueReplyPacket)

        return p.data

    def execute_command(self, command, payload):
        frame = bytearray([0xb1, 0xb2, command, *payload, 0xb6])
        self._serial_write(frame)

        self._wait_for_packet(AckReply)

    def get_is_on(self) -> bool:
        pa = self.read_value([IS_ON, 0, 0])
        return pa[2] == 1

    def get_voltage(self) -> float:
        pa = self.read_value([VOLTAGE, 0, 0])
        return unpack_uint24(pa) / 1000

    def get_current(self) -> float:
        pa = self.read_value([CURRENT, 0, 0])
        return unpack_uint24(pa) / 1000

    def get_energy(self) -> float:
        pa = self.read_value([CAP_WH, 0, 0])
        return unpack_uint24(pa) / 1000

    def get_charge(self) -> float:
        pa = self.read_value([CAP_AH, 0, 0])
        return unpack_uint24(pa) / 1000

    def get_time(self) -> datetime.timedelta:
        pa = self.read_value([TIME, 0, 0])
        return datetime.timedelta(hours=pa[0], minutes=pa[1], seconds=pa[2])

    def get_temp(self) -> int:
        pa = self.read_value([TEMP, 0, 0])
        return unpack_uint24(pa)

    def get_current_limit(self) -> float:
        pa = self.read_value([LIM_CURR, 0, 0])
        return unpack_uint16(pa) / 100

    def get_voltage_cutoff(self) -> float:
        pa = self.read_value([LIM_VOLT, 0, 0])
        return unpack_uint16(pa) / 100

    def get_timer(self) -> datetime.timedelta:
        pa = self.read_value([TIMER, 0, 0])
        return datetime.timedelta(hours=pa[0], minutes=pa[1])

    def set_current(self, current: float):
        f, i = math.modf(current)
        self.execute_command(SETCURR, [int(i), round(f * 100)])

    def set_voltage_cutoff(self, voltage: float):
        f, i = math.modf(voltage)
        self.execute_command(SETVCUT, [int(i), round(f * 100)])

    def set_timer(self, duration: datetime.timedelta):
        value = struct.pack(">H", int(duration.total_seconds()))
        self.execute_command(SETTMR, [*value])

    def reset_counters(self):
        self.execute_command(RESET_COUNTERS, [0, 0])

    def enable(self):
        self.execute_command(OUTPUT, [1, 0])

    def disable(self):
        self.execute_command(OUTPUT, [0, 0])


__all__ = [
    "DL24",
    "DL24Error",
]
