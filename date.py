# -*- coding: utf-8 -*-
"""
DART高精度甲醛传感器
"""
from machine import Pin, UART
import asyncio

def calcchecksum(data: bytes) -> int:
    """
    计算校验和
    :param data: 数据
    :return: 校验和
    """
    return (0xFF ^ (sum(data) & 0xFF))+1

class Dart:
    def __init__(self, id_: int, tx: int, rx: int):
        self._uart = UART(id_, baudrate=9600, bits=8, stop=1, tx=tx, rx=rx, timeout=0)
        self._writer = asyncio.StreamWriter(self._uart, {}) # type: ignore
        self._reader = asyncio.StreamReader(self._uart) # type: ignore
        self.has_data = asyncio.Event()
        self.has_data.clear()
        self.data = None
        self.data_mg = None
        self.mode = 0 # 0主动 1询问
        self._should_stop = False
        asyncio.create_task(self._reading_task())

    async def _reading_task(self):
        while not self._should_stop:
            data = await self._reader.readexactly(9)
            checksum = data[8]
            if checksum != calcchecksum(data[1:8]):
                print("Checksum error")
                continue
            if self.mode == 0:
                assert data[0] == 0xFF and data[1] == 0x17 and data[2] == 0x04 and data[3] == 0x00
                ch2o = int.from_bytes(data[4:6], byteorder='big')
                full = int.from_bytes(data[6:8], byteorder='big')
                assert full == 2000
                self.data = ch2o
                self.has_data.set()
            else:
                assert data[0] == 0xFF and data[1] == 0x86
                ch2o_mg = int.from_bytes(data[2:4], byteorder='big')
                ch2o = int.from_bytes(data[6:8], byteorder='big')
                self.data = ch2o
                self.data_mg = ch2o_mg
                self.has_data.set()

    async def request(self):
        self._writer.write(b'\xff\x01\x86\x00\x00\x00\x00\x00y')
        await self._writer.drain()
        # await self.has_data.wait()

    async def ask_mode(self):
        """
        询问模式
        :return: None
        """
        self._writer.write(b'\xff\x01xA\x00\x00\x00\x00F')
        await self._writer.drain()
        self.mode = 1

    async def auto_mode(self):
        """
        自动模式
        :return: None
        """
        self._writer.write(b'\xff\x01x@\x00\x00\x00\x00G')
        await self._writer.drain()
        self.mode = 0

    def deinit(self):
        self._should_stop = True
        self._uart.deinit()