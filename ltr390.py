# -*- coding: utf-8 -*-
import asyncio
from micropython import const
from machine import Pin, I2C
import time


class LTR390:
    # I2C地址
    I2C_ADDR = const(0x53)
    # 寄存器地址
    REG_MAIN_CTRL = const(0x00)
    REG_MEAS_RATE = const(0x04)
    REG_UVS_GAIN = const(0x05)
    REG_UVS_DATA = const(0x10)
    REG_ALS_DATA = const(0x0D)
    REG_INT_CFG = const(0x19)
    REG_INT_PST = const(0x1aA)
    PART_ID = const(0x06)

    # 测量模式
    MODE_ALS = const(0x02)  # ALS in Active Mode
    MODE_UVS = const(0x0A)  # UVS in Active Mode

    RESOLUTION_20BIT_TIME400MS = const(0X00)
    RESOLUTION_19BIT_TIME200MS = const(0X10)
    RESOLUTION_18BIT_TIME100MS = const(0X20)  # default
    RESOLUTION_17BIT_TIME50MS = const(0x30)
    RESOLUTION_16BIT_TIME25MS = const(0x40)
    RESOLUTION_13BIT_TIME12_5MS = const(0x50)
    RATE_25MS = const(0x0)
    RATE_50MS = const(0x1)
    RATE_100MS = const(0x2)  # default
    RATE_200MS = const(0x3)
    RATE_500MS = const(0x4)
    RATE_1000MS = const(0x5)
    RATE_2000MS = const(0x6)

    # measurement Gain Range.
    GAIN_1 = const(0x0)
    GAIN_3 = const(0x1)  # default
    GAIN_6 = const(0x2)
    GAIN_9 = const(0x3)
    GAIN_18 = const(0x4)

    def __init__(self, i2c_bus, sda_pin=21, scl_pin=22):
        """
        初始化传感器
        :param i2c_bus: I2C总线号 (0或1)
        :param sda_pin: SDA引脚
        :param scl_pin: SCL引脚
        """
        self.i2c = I2C(i2c_bus, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        self.addr = self.I2C_ADDR
        self._verify_device()
        self._init_sensor()
        self.wfac = 1.0  # 光照强度转换系数

    def _verify_device(self):
        """验证设备ID"""
        device_id = self._read_reg(self.PART_ID, 1)[0]
        if device_id != 0xB2:
            print(f"Invalid device ID: 0x{device_id:02X}, expected 0xB2, maybe a newer version.")

    def _init_sensor(self):
        """初始化传感器配置"""
        # 重置配置
        self._write_reg(self.REG_MAIN_CTRL, 0x00)
        time.sleep_ms(50)
        # 设置默认测量模式为UV
        self.set_mode(self.MODE_UVS)
        # 配置测量速率和分辨率
        # 默认设置：500ms间隔，20位分辨率
        self.set_resolution_rate(self.RESOLUTION_20BIT_TIME400MS, self.RATE_500MS)

    def get_resolution_rate(self):
        """
        获取当前分辨率和测量速率
        :return:
        """
        data = self._read_reg(self.REG_MEAS_RATE, 1)[0]
        return data & 0xF0, data & 0x0F

    def set_resolution_rate(self, resolution: int, rate: int):
        """
000, 20 Bit, Conversion time = 400ms
001, 19 Bit, Conversion time = 200ms
010, 18 Bit, Conversion time = 100ms(default)
011, 17 Bit, Conversion time = 50ms
100, 16 Bit, Conversion time = 25ms
101, 13 Bit
        :param rate:
        :param resolution: 0（16位）或 1（18位）
        """
        # if resolution not in (20, 19, 18, 17, 16, 13):
        #     raise ValueError("Invalid resolution")
        # if rate not in (25, 50, 100, 200, 500, 1000, 2000):
        #     raise ValueError("Invalid rate")
        # resolution_map = {
        #     20: "000",
        #     19: "001",
        #     18: "010",
        #     17: "011",
        #     16: "100",
        #     13: "101",
        # }
        # rate_map = {
        #     25: "000",
        #     50: "001",
        #     100: "010",
        #     200: "011",
        #     500: "100",
        #     1000: "101",
        #     2000: "110",
        # }
        self._write_reg(self.REG_MEAS_RATE, resolution | rate)
        time.sleep(0.05)

    def set_mode(self, mode):
        """
        设置测量模式
        :param mode: MODE_ALS 或 MODE_UVS
        """
        if mode not in (self.MODE_ALS, self.MODE_UVS):
            raise ValueError("Invalid mode")
        self._write_reg(self.REG_MAIN_CTRL, mode)
        self.mode = mode
        time.sleep_ms(50)  # 等待模式切换

    ########
    def set_gain(self, gain: int):
        self._write_reg(self.REG_UVS_GAIN, gain)

    def get_gain(self):
        return self._read_reg(self.REG_UVS_GAIN, 1)

    def _read_reg(self, reg, length):
        """读取寄存器"""
        return self.i2c.readfrom_mem(self.addr, reg, length)

    def _write_reg(self, reg, value):
        """写入寄存器"""
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def _read_data_reg(self):
        """读取当前模式的数据寄存器"""
        if self.mode == self.MODE_UVS:
            data = self._read_reg(self.REG_UVS_DATA, 3)
        else:
            data = self._read_reg(self.REG_ALS_DATA, 3)
        return int.from_bytes(data, 'little')

    def read_uvs(self):
        """读取紫外线数据（需要先设置为UVS模式）"""
        self._write_reg(self.REG_INT_CFG, 0x34)
        self.set_mode(self.MODE_UVS)
        raw = self._read_data_reg()
        gain = self.get_gain()
        if gain == self.GAIN_1:
            gain = 1
        elif gain == self.GAIN_3:
            gain = 3
        elif gain == self.GAIN_6:
            gain = 6
        elif gain == self.GAIN_9:
            gain = 9
        elif gain == self.GAIN_18:
            gain = 18
        re, _ = self.get_resolution_rate()
        if re == self.RESOLUTION_16BIT_TIME25MS:  # 积分时间
            re = 0.25
        elif re == self.RESOLUTION_17BIT_TIME50MS:
            re = 0.5
        elif re == self.RESOLUTION_18BIT_TIME100MS:
            re = 1
        elif re == self.RESOLUTION_19BIT_TIME200MS:
            re = 2
        elif re == self.RESOLUTION_20BIT_TIME400MS:
            re = 4
        sensitivity = 2300 * gain / 18 * re / 4
        return raw / sensitivity * self.wfac # https://esphome.io/components/sensor/ltr390

    def read_als(self):
        """读取环境光数据（需要先设置为ALS模式）"""
        self._write_reg(self.REG_INT_CFG, 0x14)
        self.set_mode(self.MODE_ALS)
        raw = self._read_data_reg()
        gain = self.get_gain()
        if gain == self.GAIN_1:
            gain = 1
        elif gain == self.GAIN_3:
            gain = 3
        elif gain == self.GAIN_6:
            gain = 6
        elif gain == self.GAIN_9:
            gain = 9
        elif gain == self.GAIN_18:
            gain = 18
        re, _ = self.get_resolution_rate()
        if re == self.RESOLUTION_16BIT_TIME25MS:  # 积分时间
            re = 0.25
        elif re == self.RESOLUTION_17BIT_TIME50MS:
            re = 0.5
        elif re == self.RESOLUTION_18BIT_TIME100MS:
            re = 1
        elif re == self.RESOLUTION_19BIT_TIME200MS:
            re = 2
        elif re == self.RESOLUTION_20BIT_TIME400MS:
            re = 4
        return 0.6 * raw / gain / re * self.wfac  # https://esphome.io/components/sensor/ltr390

    # @property
    # def data_ready(self):
    #     """检查数据是否就绪"""
    #     status = self._read_reg(self.REG_INT_PST, 1)[0]
    #     return (status & 0x08) != 0  # 检查DATA_READY位

    def set_thresh(self, low, high):  # LTR390_THRESH_UP and LTR390_THRESH_LOW
        self._write_reg(0x21, high & 0xff)
        self._write_reg(0x22, (high >> 8) & 0xff)
        self._write_reg(0x23, (high >> 16) & 0x0f)
        self._write_reg(0x24, low & 0xff)
        self._write_reg(0x25, (low >> 8) & 0xff)
        self._write_reg(0x26, (low >> 16) & 0x0f)


# 使用示例

if __name__ == '__main__':
    sensor = LTR390(0)  # 使用I2C总线0
    # 读取紫外线数据
    sensor.set_mode(sensor.MODE_UVS)
    while not sensor.data_ready:
        time.sleep(0.1)
    print(f"UV Index: {sensor.read_uvs():.2f}")
    # 读取环境光数据
    sensor.set_mode(sensor.MODE_ALS)
    while not sensor.data_ready:
        time.sleep(0.1)
    print(f"ALS: {sensor.read_als():.2f} lux")
