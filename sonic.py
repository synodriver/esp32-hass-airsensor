# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
from machine import Pin, time_pulse_us
import time
import asyncio


# trig 18 echo 19
async def measure(t: int, e: int, timeoot=0.5, speed_of_sound=340) -> float:
    trigger = Pin(t, Pin.OUT)
    echo = Pin(e, Pin.IN, Pin.PULL_DOWN)
    trigger.value(0)
    time.sleep_us(10)
    trigger.value(1)
    time.sleep_us(20)
    trigger.value(0)
    timeout_us = timeoot * 1_000_000
    s1 = time.ticks_us()
    while echo.value() == 0 and time.ticks_diff(time.ticks_us(), s1) < timeout_us:
        await asyncio.sleep(0)
    if echo.value() == 0:
        print(f"early 1 {time.ticks_diff(time.ticks_us(), s1)} {timeout_us}")
        return 0  # timeout gets nothing
    # ensure start instead of timeout
    start = time.ticks_us()
    while echo.value() == 1 and time.ticks_diff(time.ticks_us(), s1) < timeout_us:
        await asyncio.sleep(0)
    if echo.value() == 1:
        print("early 2")
        return 0
    end = time.ticks_us()
    delta = time.ticks_diff(end, start) / 1000000
    return delta * speed_of_sound / 2


class HCSR04:
    # echo_timeout_us is based in chip range limit (400cm)
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)
        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)
    def _send_pulse_and_wait(self):
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
            print(f"pulse_time: {pulse_time}")
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex
    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.
        """
        pulse_time = self._send_pulse_and_wait()
        mm = pulse_time * 100 // 582
        return mm
    def distance_cm(self):
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) / 29.1
        return cms
