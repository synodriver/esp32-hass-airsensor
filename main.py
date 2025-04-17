# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
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
    'wifi_ssid': '',#
    'wifi_password': '',
    'ap_ssid': 'ESP32-Config',
    'ap_password': '',
    'web_port': 80,
    'connect_timeout': 10,
    "broker_ip": "192.168.0.27",
    "broker_port": 1883,
    "broker_user": "",
    "broker_password": "",
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

#ap = network.WLAN(network.AP_IF)  # fail back

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
            "value_template": "{{ value_json.temperature}}",
            "unique_id": "%s.temperature" % object_id
        },
        "%s.humidity" % object_id: {
            "platform": "sensor",
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "value_template": "{{ value_json.humidity}}",
            "unique_id": "%s.humidity" % object_id
        },
        "%s.tvoc" % object_id: {
            "platform": "sensor",
            "device_class": "volatile_organic_compounds",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.voc}}",
            "unique_id": "%s.tvoc" % object_id
        },
        "%s.pm25" % object_id: {
            "platform": "sensor",
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.pm25}}",
            "unique_id": "%s.pm25" % object_id
        },
        "%s.pm10" % object_id: {
            "platform": "sensor",
            "device_class": "pm10",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.pm10}}",
            "unique_id": "%s.pm10" % object_id
        },
        "%s.ch2o" % object_id: {
            "platform": "sensor",
            "icon": "mdi:chemical-weapon",
            "name": "甲醛",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.ch2o}}",
            "unique_id": "%s.ch2o" % object_id
        },
        "%s.co2" % object_id: {
            "platform": "sensor",
            "device_class": "carbon_dioxide",
            "unit_of_measurement": "ppm",
            "value_template": "{{ value_json.co2}}",
            "unique_id": "%s.co2" % object_id
        },

    },
    "state_topic": state_topic,
    "availability_topic": availability_topic,
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
print(config)
# The rest of the configuration
client = MQTTClient(config)


# For MQTT 5 and 3.1.1 support
# def on_message(topic, msg, retained, properties=None):
#     print((topic, msg, retained, properties))


async def read_sensors(client: MQTTClient):
    print("Reading sensors...")
    try:
        airmod = AirMod(2,17, 16)
    except Exception as e:
        print(f"create uart fail: {e}")
        return
    print("Connected to uart")
    while True:
        print("read sensor")
        await airmod.has_data.wait()
        airmod.has_data.clear()
        data = airmod.data
        asyncio.create_task(client.publish(state_topic.encode(), json.dumps(data).encode(), qos=1))  # do not block


async def handle_online(client: MQTTClient):
    #global ap
    while True:
        await client.up.wait()
        client.up.clear()
        #await setup_ap(False)
        await client.publish(availability_topic.encode(), b"online", retain=True, qos=1)


async def handle_offline():
    while True:
        await client.down.wait()
        client.down.clear()
        #await setup_ap(True)


async def main(client: MQTTClient):
    try:
        print("in main")
        await client.connect()
        print("Connected to wifi.")
        await client.up.wait()
        client.up.clear()
        print("client ready")
        await client.publish(discovery_topic.encode(), json.dumps(discovery_payload).encode(), retain=True, qos=1)
        await client.publish(availability_topic.encode(), b"online", retain=True, qos=1)
        print("online info published")
        #asyncio.create_task(handle_online(client))
        #asyncio.create_task(handle_offline())
        await read_sensors(client)
    except OSError as e:
        print(f"Connection failed: {str(e)}.")
        return


try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
