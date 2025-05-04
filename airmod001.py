# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
import asyncio

from machine import UART


class AirMod:
    def __init__(self, id_: int, tx: int, rx: int):
        try:
            self._uart = UART(id_, baudrate=9600, bits=8, stop=1, tx=tx, rx=rx, timeout=0)
            # self._writer = asyncio.StreamWriter(self._uart, {}) # type: ignore
        except:
            print("UART error")
            raise
        self._reader = asyncio.StreamReader(self._uart)  # type: ignore
        self._should_stop = False
        self.data = None
        self.has_data = asyncio.Event()
        self.has_data.clear()
        asyncio.create_task(self._reading_task())

    async def _reading_task(self):
        while not self._should_stop:
            res = await self._reader.readexactly(17)
            if res[0] != 0x3C or res[1] != 0x02:
                print("header error")
                continue
            checksum = res[16]
            tmp = sum(res[:16]) & 0xFF
            if checksum != tmp:
                print("checksum error")
                continue
            co2 = int.from_bytes(res[2:4], "big")
            ch2o = int.from_bytes(res[4:6], "big")
            voc = int.from_bytes(res[6:8], "big")
            pm25 = int.from_bytes(res[8:10], "big")
            pm10 = int.from_bytes(res[10:12], "big")
            if res[12] & 0x80:
                # <0
                tempreture = -(float(res[12] & 0x7F) + res[13] / 10)
            else:
                tempreture = float(res[12] & 0x7F) + res[13] / 10
            humidity = float(res[14]) + res[15] / 10
            self.data = {
                "temperature": tempreture,
                "humidity": humidity,
                "voc": voc,
                "pm25": pm25,
                "pm10": pm10,
                "ch2o": ch2o,
                "co2": co2
            }
            self.has_data.set()

    def deinit(self):
        self._should_stop = True
        self._uart.deinit()