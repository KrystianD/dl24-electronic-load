import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import cast

import serial

from dl24 import DL24Error
from .ITransport import ITransport

DefaultReadTimeout = 5


class DL24SerialError(DL24Error):
    def __init__(self, e: Exception):
        super().__init__(f"serial error: {e}")


class TransportSerial(ITransport):
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = DefaultReadTimeout) -> None:
        self._serial = serial.Serial(port=port,
                                     timeout=timeout,
                                     write_timeout=timeout,
                                     baudrate=baudrate,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE)
        self._timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=1)

    def close(self) -> None:
        self._executor.shutdown()
        self._serial.close()

    async def write(self, data: bytes) -> None:
        try:
            self._serial.flushOutput()
            self._serial.flushInput()
            self._serial.write(data)
        except serial.SerialException as e:
            raise DL24SerialError(e)

    async def read(self, size: int) -> bytes:
        try:
            data = await asyncio.get_event_loop().run_in_executor(self._executor, self._serial.read, size)
            if len(data) == 0:
                raise asyncio.exceptions.TimeoutError()
            return cast(bytes, data)
        except serial.SerialException as e:
            raise DL24SerialError(e)

    def flush(self):
        self._serial.flushInput()


__all__ = [
    "TransportSerial",
]
