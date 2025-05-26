# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
import gc
import binascii
import hashlib
import os
gc.collect()

# import aiohttp
import esp
import esp32
gc.collect()


from ltr390 import LTR390
from bmp3xx import BMP3XX_I2C
from airmod001 import AirMod

import asyncio
import json
import machine
from mqtt_as import MQTTClient, config
gc.collect()

# 默认配置
DEFAULT_CONFIG = {
    'wifi_ssid': '',  #
    'wifi_password': '',
    'ap_ssid': 'ESP32-Config',
    'ap_password': '',
    'web_port': 80,
    'connect_timeout': 10,
    "broker_ip": "192.168.0.27",
    "broker_port": 1883,
    "broker_user": "",
    "broker_password": "",
    "debug": True
}

# 配置文件路径
CONFIG_FILE = 'config.json'


def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # 合并默认配置，确保所有键都存在
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
            return config
    except:
        # 文件不存在或读取错误，创建默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)


netconfig = load_config()
debug = netconfig["debug"]


def dprint(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


BROKER_IP = netconfig["broker_ip"]
BROKER_PORT = netconfig["broker_port"]
BROKER_USER = netconfig["broker_user"]
BROKER_PASSWORD = netconfig["broker_password"]

discovery_prefix = "homeassistant"
component = "device"
object_id = binascii.hexlify(machine.unique_id()).decode()

discovery_topic = "%s/%s/%s/config" % (discovery_prefix, component, object_id)
availability_topic = "%s/%s/%s/availability" % (discovery_prefix, component, object_id)
state_topic = "%s/%s/%s/state" % (discovery_prefix, component, object_id)
command_topic = "%s/%s/%s/set" % (discovery_prefix, component, object_id)
log_topic = "%s/%s/%s/log" % (discovery_prefix, component, object_id) # log topic for debug
# ap = network.WLAN(network.AP_IF)  # fail back

# async def setup_ap(activate=True):
#     """设置或关闭AP热点模式"""
#     if activate:
#         print(f"设置AP热点: {netconfig['ap_ssid']}")
#         ap.active(True)
#         ap.config(essid=netconfig['ap_ssid'], password=netconfig['ap_password'], authmode=network.AUTH_WPA_WPA2_PSK)
#
#         while not ap.active():
#             await asyncio.sleep(0.5)
#         ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
#         print('\nAP热点已激活!')
#         print('AP配置:', ap.ifconfig())
#     else:
#         print('关闭AP热点...')
#         ap.active(False)
#
# 可以通过mqtt的number组件来设置
# runtime_cfg = {
#     "update_interval": 1,  # seconds
# }

discovery_payload = {
    "device": {
        "identifiers": object_id,
        "name": "十合一传感器模组",
        "manufacturer": "Synodriver Corp",
        "model": "synosensor 01",
        "sw_version": "0.1",
        "serial_number": object_id,
        "hw_version": "0.1"
    },
    "origin": {
        "name": "7in1sensor",
        "sw_version": "0.1",
        "support_url": "https://github.com/synodriver",
    },
    "components": {
        "%s.temperature" % object_id: {
            "platform": "sensor",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.temperature}}",
            "unique_id": "%s.temperature" % object_id
        },
        "%s.humidity" % object_id: {
            "platform": "sensor",
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "value_template": "{{value_json.humidity}}",
            "unique_id": "%s.humidity" % object_id
        },
        "%s.tvoc" % object_id: {
            "platform": "sensor",
            "device_class": "volatile_organic_compounds",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{value_json.voc}}",
            "unique_id": "%s.tvoc" % object_id
        },
        "%s.pm25" % object_id: {
            "platform": "sensor",
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{value_json.pm25}}",
            "unique_id": "%s.pm25" % object_id
        },
        "%s.pm10" % object_id: {
            "platform": "sensor",
            "device_class": "pm10",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{value_json.pm10}}",
            "unique_id": "%s.pm10" % object_id
        },
        "%s.ch2o" % object_id: {
            "platform": "sensor",
            "icon": "mdi:chemical-weapon",
            "name": "甲醛",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{value_json.ch2o}}",
            "unique_id": "%s.ch2o" % object_id
        },
        "%s.co2" % object_id: {
            "platform": "sensor",
            "device_class": "carbon_dioxide",
            "unit_of_measurement": "ppm",
            "value_template": "{{value_json.co2}}",
            "unique_id": "%s.co2" % object_id
        },
        "%s.light" % object_id: {
            "platform": "sensor",
            "device_class": "illuminance",
            "unit_of_measurement": "lx",
            "value_template": "{{value_json.light}}",
            "unique_id": "%s.light" % object_id
        },
        "%s.uv" % object_id: {
            "platform": "sensor",
            "name": "紫外线指数",
            "unit_of_measurement": "UV index",
            "value_template": "{{value_json.uv}}",
            "unique_id": "%s.uv" % object_id
        },
        "%s.pressure" % object_id: {
            "platform": "sensor",
            "device_class": "pressure",
            "unit_of_measurement": "kPa",
            "value_template": "{{value_json.pressure}}",
            "unique_id": "%s.pressure" % object_id
        },
        "%s.pressure_temperature" % object_id: {
            "platform": "sensor",
            "name": "气压传感器内部温度",
            "enabled_by_default": False,
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.pressure_temperature}}",
            "unique_id": "%s.pressure_temperature" % object_id
        },

        "%s.ip_address" % object_id: {
            "platform": "sensor",
            "icon": "mdi:ip",
            "name": "IP地址",
            "value_template": "{{value_json.ip_address}}",
            "unique_id": "%s.ip_address" % object_id,
            "entity_category": "diagnostic"
        },
        "%s.ssid" % object_id: {
            "platform": "sensor",
            "icon": "mdi:wifi",
            "name": "SSID",
            "value_template": "{{value_json.ssid}}",
            "unique_id": "%s.ssid" % object_id,
            "entity_category": "diagnostic"
        },
        "%s.essid" % object_id: {
            "platform": "sensor",
            "icon": "mdi:wifi",
            "name": "ESSID",
            "value_template": "{{value_json.essid}}",
            "unique_id": "%s.essid" % object_id.encode(),
            "entity_category": "diagnostic"
        },
        "%s.mac_address" % object_id: {
            "platform": "sensor",
            "icon": "mdi:wifi",
            "name": "MAC",
            "value_template": "{{value_json.mac_address}}",
            "unique_id": "%s.mac_address" % object_id,
            "entity_category": "diagnostic"
        },
        "%s.dns_address" % object_id: {
            "platform": "sensor",
            "icon": "mdi:dns",
            "name": "DNS",
            "value_template": "{{value_json.dns_address}}",
            "unique_id": "%s.dns_address" % object_id,
            "entity_category": "diagnostic"
        },
        "%s.txpower" % object_id: {
            "platform": "sensor",
            "icon": "mdi:wifi",
            "name": "发射功率",
            "value_template": "{{value_json.txpower}}",
            "unique_id": "%s.txpower" % object_id,
            "unit_of_measurement": "dBm",
            "entity_category": "diagnostic"
        },
        "%s.flash_size" % object_id: {
            "platform": "sensor",
            "icon": "mdi:file",
            "name": "flash总大小",
            "device_class": "data_size",
            "value_template": "{{value_json.flash_size}}",
            "unique_id": "%s.flash_size" % object_id,
            "unit_of_measurement": "B",
            "entity_category": "diagnostic"
        },
        "%s.raw_temperature" % object_id: {
            "platform": "sensor",
            "icon": "mdi:cpu-32-bit",
            "name": "核心温度",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.raw_temperature}}",
            "unique_id": "%s.raw_temperature" % object_id,
            "entity_category": "diagnostic"
        },
        "%s.flash_available" % object_id: {
            "platform": "sensor",
            "icon": "mdi:file-alert",
            "name": "flash剩余空间",
            "device_class": "data_size",
            "value_template": "{{value_json.flash_available}}",
            "unique_id": "%s.flash_available" % object_id,
            "unit_of_measurement": "B",
            "entity_category": "diagnostic"
        },
        "%s.free_memory" % object_id: {
            "platform": "sensor",
            "icon": "mdi:memory",
            "name": "剩余内存",
            "device_class": "data_size",
            "value_template": "{{value_json.free_memory}}",
            "unique_id": "%s.free_memory" % object_id,
            "unit_of_measurement": "B",
            "entity_category": "diagnostic"
        },

        "%s.uvs_resolution" % object_id: {
            "platform": "select",
            "icon": "mdi:numeric",
            "name": "紫外线传感器分辨率(位)",
            "value_template": "{{value_json.uvs_resolution}}",
            "unique_id": "%s.uvs_resolution" % object_id,
            "options": ["20", "19", "18", "17", "16", "13"],  # option list must be List[str]
            # "entity_category": "diagnostic",
            "command_template": "{\"uvs_resolution\":  \"{{value}}}\"",
        },
        "%s.uvs_rate" % object_id: {
            "platform": "select",
            "icon": "mdi:numeric",
            "name": "紫外线传感器测量速率",
            "value_template": "{{value_json.uvs_rate}}",
            "unique_id": "%s.uvs_rate" % object_id,
            "options": ["25ms", "50ms", "100ms", "200ms", "500ms", "1000ms", "2000ms"],
            "command_template": "{\"uvs_rate\":  \"{{value}}\"}",
        },
        "%s.uvs_gain" % object_id: {
            "platform": "select",
            "icon": "mdi:numeric",
            "name": "紫外线传感器增益",
            "value_template": "{{value_json.uvs_gain}}",
            "unique_id": "%s.uvs_gain" % object_id,
            "options": ["1", "3", "6", "9", "18"],
            "command_template": "{\"uvs_gain\":  \"{{value}}\"}",
        },
        "%s.uvs_sensitivity_max" % object_id: {
            "platform": "number",
            "icon": "mdi:numeric",
            "name": "紫外线传感器sensitivity_max",
            "value_template": "{{value_json.uvs_sensitivity_max}}",
            "unique_id": "%s.uvs_sensitivity_max" % object_id,
            "min": 0,
            "max": 10000,
            "step": 1,
            "command_template": "{\"uvs_sensitivity_max\":  {{value}}}",
        },
        "%s.Wfac" % object_id: {
            "platform": "number",
            "icon": "mdi:numeric",
            "name": "紫外线传感器Wfac",
            "value_template": "{{value_json.Wfac}}",
            "unique_id": "%s.Wfac" % object_id,
            "min": 1,
            "max": 10,
            "step": 0.01,
            "command_template": "{\"Wfac\":  {{value}}}",
        },
        "%s.altitude" % object_id: {
            "platform": "number",
            "icon": "mdi:terrain",
            "name": "参考海拔高度",
            "value_template": "{{value_json.altitude}}",
            "unique_id": "%s.altitude" % object_id,
            "min": -1000000,
            "max": 1000000,
            "step": 0.1,
            "command_template": "{\"altitude\":  {{value}}}",
        },
        "%s.reset" % object_id: {
            "platform": "button",
            "name": "重启",
            "icon": "mdi:restart",
            "unique_id": "%s.reset" % object_id,
            "entity_category": "diagnostic",
            "command_template": "{\"reset\": \"{{value}}\"}",
        }
    },
    "state_topic": state_topic,
    "availability_topic": availability_topic,
    "command_topic": command_topic,
    "qos": 1
}

config['mqttv5'] = True
# Optional: Set the properties for the connection
config['mqttv5_con_props'] = {
    0x11: 3600,  # Session Expiry Interval
}
config["server"] = BROKER_IP
config["port"] = BROKER_PORT
config["user"] = BROKER_USER
config["password"] = BROKER_PASSWORD
config["will"] = [availability_topic.encode(), b"offline", True, 1]
config["keepalive"] = 60
config["queue_len"] = 4
config["ssid"] = netconfig["wifi_ssid"]
config["wifi_pw"] = netconfig["wifi_password"]
dprint(config)
# The rest of the configuration
client = MQTTClient(config)

# For MQTT 5 and 3.1.1 support
# def on_message(topic, msg, retained, properties=None):
#     print((topic, msg, retained, properties))

lock = asyncio.Lock()
sensor_state = {}  # global sensor state


async def update_sensor_state(value: dict):
    global sensor_state
    async with lock:
        sensor_state.update(value)
        # print(f"Sensor {sensor} updated to {value}")


async def read_airdmod(airmod: AirMod):
    while True:
        await airmod.has_data.wait()
        airmod.has_data.clear()
        data = airmod.data
        dprint("got airmod data")
        await update_sensor_state(data)


async def read_ltr390(ltr390: LTR390):
    while True:
        data = await get_ltr390_data(ltr390)
        dprint("got ltr390 data")
        await update_sensor_state(data)
        await asyncio.sleep_ms(200)  # Avoid busy waiting


async def read_bmp390(bmp390: BMP3XX_I2C):
    while True:
        data = {
            "pressure": bmp390.pressure / 1000,
            "pressure_temperature": bmp390.temperature,
            "altitude": bmp390.altitude
        }
        dprint("got bmp390 data")
        await update_sensor_state(data)
        await asyncio.sleep(1)  # Avoid busy waiting


async def read_wifi(client: MQTTClient):
    while True:
        data = get_wifi_data(client)
        dprint("got wifi data")
        await update_sensor_state(data)
        await asyncio.sleep(30)


async def read_esp_info():
    while True:
        flash_size = esp.flash_size()  # byte
        raw_temperature = (esp32.raw_temperature() - 32) / 1.8
        size_info = os.statvfs('/flash')
        flash_available = size_info[0] * size_info[3]
        free = gc.mem_free()
        await update_sensor_state({
            "flash_size": flash_size,
            "raw_temperature": raw_temperature,
            "flash_available": flash_available,
            "free_memory": free,
        })
        await asyncio.sleep(60)


async def publish_data(client: MQTTClient):
    await asyncio.sleep(5)  # Wait for the first data in sensor state
    while True:
        await client.publish(state_topic.encode(), json.dumps(sensor_state).encode(), qos=1)  # do not block
        await asyncio.sleep(1)


# async def read_sensors(client: MQTTClient, airmod: AirMod, ltr390: LTR390):
#     while True:
#         await airmod.has_data.wait()
#         airmod.has_data.clear()
#         data = airmod.data
#         dprint("got airmod data")
#         data.update(get_wifi_data(client))
#         data.update(await get_ltr390_data(ltr390))
#         dprint("got ltr390 data")
#         asyncio.create_task(client.publish(state_topic.encode(), json.dumps(data).encode(), qos=1))  # do not block

def get_wifi_data(client: MQTTClient) -> dict:
    attr_data = {"ip_address": client._sta_if.ifconfig()[0],
                 "ssid": client._sta_if.config('ssid'),
                 "essid": client._sta_if.config('essid'),
                 "mac_address": binascii.hexlify(client._sta_if.config('mac')).upper(),
                 "dns_address": client._sta_if.ifconfig()[3],
                 "txpower": client._sta_if.config('txpower'),
                 }
    return attr_data


async def get_ltr390_data(ltr390: LTR390) -> dict:
    re, rate = ltr390.get_resolution_rate()
    if re == LTR390.RESOLUTION_13BIT_TIME12_5MS:
        re = "13"
    elif re == LTR390.RESOLUTION_16BIT_TIME25MS:
        re = "16"
    elif re == LTR390.RESOLUTION_17BIT_TIME50MS:
        re = "17"
    elif re == LTR390.RESOLUTION_18BIT_TIME100MS:
        re = "18"
    elif re == LTR390.RESOLUTION_19BIT_TIME200MS:
        re = "19"
    elif re == LTR390.RESOLUTION_20BIT_TIME400MS:
        re = "20"

    if rate == LTR390.RATE_25MS:
        rate = "25ms"
    elif rate == LTR390.RATE_50MS:
        rate = "50ms"
    elif rate == LTR390.RATE_100MS:
        rate = "100ms"
    elif rate == LTR390.RATE_200MS:
        rate = "200ms"
    elif rate == LTR390.RATE_500MS:
        rate = "500ms"
    elif rate == LTR390.RATE_1000MS:
        rate = "1000ms"
    elif rate == LTR390.RATE_2000MS:
        rate = "2000ms"
    gain = ltr390.get_gain()
    if gain == LTR390.GAIN_1:
        gain = "1"
    elif gain == LTR390.GAIN_3:
        gain = "3"
    elif gain == LTR390.GAIN_6:
        gain = "6"
    elif gain == LTR390.GAIN_9:
        gain = "9"
    elif gain == LTR390.GAIN_18:
        gain = "18"
    attr_data = {
        "light": await ltr390.read_als(),
        "uv": await ltr390.read_uvs(),
        "uvs_resolution": re,
        "uvs_rate": rate,
        "uvs_gain": gain,
        "uvs_sensitivity_max": ltr390.sensitivity_max,
        "Wfac": ltr390.wfac,
    }
    return attr_data


async def handle_online(client: MQTTClient):
    # global ap
    while True:
        await client.up.wait()
        client.up.clear()
        # await setup_ap(False)
        await client.publish(availability_topic.encode(), b"online", retain=True, qos=1)
        await client.subscribe(command_topic.encode(), qos=1)


async def handle_offline():
    while True:
        await client.down.wait()
        client.down.clear()
        # await setup_ap(True)


async def listen_mqtt(client: MQTTClient, ltr390: LTR390, bmp390: BMP3XX_I2C):
    resolution_map = {
        20: LTR390.RESOLUTION_20BIT_TIME400MS,
        19: LTR390.RESOLUTION_19BIT_TIME200MS,
        18: LTR390.RESOLUTION_18BIT_TIME100MS,
        17: LTR390.RESOLUTION_17BIT_TIME50MS,
        16: LTR390.RESOLUTION_16BIT_TIME25MS,
        13: LTR390.RESOLUTION_13BIT_TIME12_5MS,
    }
    rate_map = {
        "25ms": LTR390.RATE_25MS,
        "50ms": LTR390.RATE_50MS,
        "100ms": LTR390.RATE_100MS,
        "200ms": LTR390.RATE_200MS,
        "500ms": LTR390.RATE_500MS,
        "1000ms": LTR390.RATE_1000MS,
        "2000ms": LTR390.RATE_2000MS,
    }
    async for topic, msg, retained, properties in client.queue:
        if topic == command_topic.encode():
            dprint(f"Received command: {msg.decode()}")
            try:
                payload = json.loads(msg.decode())
            except:
                dprint("Invalid JSON payload received in command topic")
                continue
            if "uvs_resolution" in payload:
                dprint("change uvs_resolution")
                uvs_resolution: int = int(payload["uvs_resolution"])
                _, rate = ltr390.get_resolution_rate()
                ltr390.set_resolution_rate(resolution_map[uvs_resolution], rate)
            if "uvs_rate" in payload:
                dprint("change uvs_rate")
                uvs_rate: str = payload["uvs_rate"]
                resolution, _ = ltr390.get_resolution_rate()
                ltr390.set_resolution_rate(resolution, rate_map[uvs_rate])
            if "Wfac" in payload:
                dprint("change Wfac")
                Wfac: float = payload["Wfac"]
                ltr390.wfac = Wfac
            if "uvs_gain" in payload:
                dprint("change uvs_gain")
                uvs_gain: int = int(payload["uvs_gain"])
                if uvs_gain == 1:
                    uvs_gain = LTR390.GAIN_1
                elif uvs_gain == 3:
                    uvs_gain = LTR390.GAIN_3
                elif uvs_gain == 6:
                    uvs_gain = LTR390.GAIN_6
                elif uvs_gain == 9:
                    uvs_gain = LTR390.GAIN_9
                elif uvs_gain == 18:
                    uvs_gain = LTR390.GAIN_18
                ltr390.set_gain(uvs_gain)
            if "uvs_sensitivity_max" in payload:
                dprint("change uvs_sensitivity_max")
                uvs_sensitivity_max = payload["uvs_sensitivity_max"]
                ltr390.sensitivity_max = uvs_sensitivity_max
            if "altitude" in payload:  # 气压传感器设置当前海拔
                dprint("change altitude")
                altitude: float = payload["altitude"]
                while not bmp390.begin():
                    dprint('Please check that the device is properly connected')
                    await asyncio.sleep(3)
                while not bmp390.set_common_sampling_mode(BMP3XX_I2C.ULTRA_PRECISION):
                    dprint('Set samping mode fail, retrying...')
                    await asyncio.sleep(3)
                if bmp390.calibrated_absolute_difference(altitude):
                    dprint("Absolute difference base value set successfully!")
            if "reset" in payload:
                dprint("reset")
                machine.reset()
            if "verify" in payload:  # {"file": filename, "verify": true}
                dprint("verify")
                md5 = hashlib.md5()
                with open(payload["file"], "rb") as f:
                    while data := f.read(100):
                        md5.update(data)
                ret = binascii.hexlify(md5.digest())
                await client.publish(log_topic.encode(), ret)
                continue
            if "file" in payload: # {"file": filename, "content": "base64 content or text", "bin": False, "url": "http://xxx"}
                dprint("update")
                filename = payload["file"]
                content = payload.get("content", None)
                bin_ = payload.get("bin", False)
                url = payload.get("url", None)
                if not content and not url:
                    os.remove(filename)
                    continue
                if url:
                    try:
                        import aiohttp
                        with open(filename, "wb") as f:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url) as response:
                                    while chunk := await response.read(100):  # type: ignore
                                        f.write(chunk)
                    except Exception as e:  # 可能内存不够
                        await client.publish(log_topic.encode(), str(e).encode())
                    continue
                if bin_:
                    with open(filename, "wb") as f:
                        f.write(binascii.a2b_base64(content))
                else:
                    with open(filename, "w") as f:
                        f.write(content)
                dprint("update done")


async def main(client: MQTTClient):
    try:
        p23 = machine.Pin(23, machine.Pin.OUT)  # TSX0108E使能，高电平启动，但是要等开完机才能高电平，否则会死锁
        p23.value(0)
        await asyncio.sleep(2)
        p23.value(1)
        dprint("pullup oe")
        await client.connect()
        dprint("Connected to wifi.")
        await client.up.wait()
        client.up.clear()
        dprint("client ready")
        await client.subscribe(command_topic.encode(), qos=1)

        await client.publish(discovery_topic.encode(), json.dumps(discovery_payload).encode(), retain=True, qos=1)
        await client.publish(availability_topic.encode(), b"online", retain=True, qos=1)
        dprint("online info published")
        try:
            airmod = AirMod(1, 17, 16)
        except Exception as e:
            dprint(f"create uart fail: {e}")
            await client.publish(log_topic.encode(), f"create uart fail: {e}".encode())
            return
        dprint("Connected to airmod uart")
        await client.publish(log_topic.encode(), b"Connected to airmod uart")
        try:
            i2c = machine.I2C(1, sda=machine.Pin(18), scl=machine.Pin(19), freq=400000)
            ltr390 = LTR390(i2c, LTR390.GAIN_18, 1400, debug)
            ltr390.set_thresh(5, 20)
        except Exception as e:
            dprint(f"create ltr390 iic fail: {e}")
            await client.publish(log_topic.encode(), f"create ltr390 iic fail: {e}".encode())
            return
        dprint("Connected to ltr390 iic uv sensor")
        await client.publish(log_topic.encode(), b"Connected to ltr390 iic uv sensor")
        try:
            i2c2 = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=40000)
            bmp390 = BMP3XX_I2C(i2c2, 0x77, debug)
            while not bmp390.begin():
                dprint('Please check that the device is properly connected')
                await asyncio.sleep(3)
            while not bmp390.set_common_sampling_mode(BMP3XX_I2C.ULTRA_PRECISION):
                dprint('Set samping mode fail, retrying...')
                await asyncio.sleep(3)
            if bmp390.calibrated_absolute_difference(280.0):
                dprint("Absolute difference base value set successfully!")
        except Exception as e:
            dprint(f"create bmp390 iic fail: {e}")
            await client.publish(log_topic.encode(), f"create bmp390 iic fail: {e}".encode())
            return
        dprint("Connected to bmp390 iic pressure sensor")
        await client.publish(log_topic.encode(), b"Connected to bmp390 iic pressure sensor")
        t1 = asyncio.create_task(handle_online(client))
        # asyncio.create_task(handle_offline())
        t2 = asyncio.create_task(listen_mqtt(client, ltr390, bmp390))
        t3 = asyncio.create_task(read_airdmod(airmod))
        t4 = asyncio.create_task(read_ltr390(ltr390))
        t5 = asyncio.create_task(read_wifi(client))
        t6 = asyncio.create_task(read_bmp390(bmp390))
        t7 = asyncio.create_task(read_esp_info())
        t8 = asyncio.create_task(publish_data(client))
        await asyncio.gather(t1, t2, t3, t4, t5, t6, t7, t8)
        # await read_sensors(client, airmod, ltr390)
    except OSError as e:
        dprint(f"Connection failed: {str(e)}.")
        return


try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()

