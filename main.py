# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
import binascii

from ltr390 import LTR390

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

import ujson as json
import network
import machine
from mqtt_as import MQTTClient, config
from ubinascii import hexlify

from airmod001 import AirMod

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
object_id = hexlify(machine.unique_id()).decode()

discovery_topic = "%s/%s/%s/config" % (discovery_prefix, component, object_id)
availability_topic = "%s/%s/%s/availability" % (discovery_prefix, component, object_id)
state_topic = "%s/%s/%s/state" % (discovery_prefix, component, object_id)
command_topic = "%s/%s/%s/set" % (discovery_prefix, component, object_id)

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
        "name": "synosensor",
        "manufacturer": "Synodriver Corp",
        "model": "synosensor 01",
        "sw_version": "0.1",
        "serial_number": "1145141919810",
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


async def read_sensors(client: MQTTClient, airmod: AirMod, ltr390: LTR390):
    while True:
        await airmod.has_data.wait()
        airmod.has_data.clear()
        data = airmod.data
        dprint("got airmod data")
        data.update(get_wifi_data(client))
        data.update(await get_ltr390_data(ltr390))
        dprint("got ltr390 data")
        asyncio.create_task(client.publish(state_topic.encode(), json.dumps(data).encode(), qos=1))  # do not block


def get_wifi_data(client: MQTTClient):
    attr_data = {"ip_address": client._sta_if.ifconfig()[0],
                 "ssid": client._sta_if.config('ssid'),
                 "essid": client._sta_if.config('essid'),
                 "mac_address": binascii.hexlify(client._sta_if.config('mac')).upper(),
                 "dns_address": client._sta_if.ifconfig()[3],
                 "txpower": client._sta_if.config('txpower'),
                 }
    return attr_data


async def get_ltr390_data(ltr390: LTR390):
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


async def handle_offline():
    while True:
        await client.down.wait()
        client.down.clear()
        # await setup_ap(True)


async def listen_mqtt(client: MQTTClient, ltr390: LTR390):
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
            payload = json.loads(msg.decode())
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
            return
        dprint("Connected to airmod uart")
        try:
            ltr390 = LTR390(1, 18, 19, LTR390.GAIN_18, debug)
            ltr390.set_thresh(5, 20)
        except Exception as e:
            dprint(f"create ltr390 iic fail: {e}")
            return
        dprint("Connected to ltr390 iic uv sensor")
        # asyncio.create_task(handle_online(client))
        # asyncio.create_task(handle_offline())
        asyncio.create_task(listen_mqtt(client, ltr390))
        await read_sensors(client, airmod, ltr390)
    except OSError as e:
        dprint(f"Connection failed: {str(e)}.")
        return


try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
