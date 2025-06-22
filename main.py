# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2025 synodriver <diguohuangjiajinweijun@gmail.com>
"""
import gc
import binascii
import hashlib
import os
import sys
import ota.rollback

gc.collect()
ota.rollback.cancel()

# import aiohttp
import esp
import esp32
gc.collect()

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

device_name = "template_device"  # 设备名称
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
        "name": device_name,
        "manufacturer": "Synodriver Corp",
        "model": "synosensor 01",
        "sw_version": "0.1",
        "serial_number": object_id,
        "hw_version": "0.1"
    },
    "origin": {
        "name": device_name,
        "sw_version": "0.1",
        "support_url": "https://github.com/synodriver",
    },
    "components": {
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

sensor_state = {}  # global sensor state


async def update_sensor_state(value: dict):
    global sensor_state
    sensor_state.update(value)
        # print(f"Sensor {sensor} updated to {value}")

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

def get_wifi_data(client: MQTTClient) -> dict:
    attr_data = {"ip_address": client._sta_if.ifconfig()[0],
                 "ssid": client._sta_if.config('ssid'),
                 "essid": client._sta_if.config('essid'),
                 "mac_address": binascii.hexlify(client._sta_if.config('mac')).upper(),
                 "dns_address": client._sta_if.ifconfig()[3],
                 "txpower": client._sta_if.config('txpower'),
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


async def listen_mqtt(client: MQTTClient):
    async for topic, msg, retained, properties in client.queue:
        if topic == command_topic.encode():
            dprint(f"Received command: {msg.decode()}")
            try:
                payload = json.loads(msg.decode())
            except:
                dprint("Invalid JSON payload received in command topic")
                continue
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
                        gc.collect()
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
            if "ota" in payload: #  {"ota": True, "url": "micropython.bin"}
                try:
                    gc.collect()
                    import ota.update
                    gc.collect()
                    ota.update.from_file(payload["url"], reboot=True)
                except Exception as e:  # 可能内存不够
                    await client.publish(log_topic.encode(), str(e).encode())


async def main(client: MQTTClient):
    try:
        await client.connect()
        dprint("Connected to wifi.")
        await client.up.wait()
        client.up.clear()
        dprint("client ready")
        await client.publish(log_topic.encode(), f"mpy version {sys.version}".encode())
        await client.subscribe(command_topic.encode(), qos=1)

        await client.publish(discovery_topic.encode(), json.dumps(discovery_payload).encode(), retain=True, qos=1)
        await client.publish(availability_topic.encode(), b"online", retain=True, qos=1)
        dprint("online info published")
        t1 = asyncio.create_task(handle_online(client))
        # asyncio.create_task(handle_offline())
        t2 = asyncio.create_task(listen_mqtt(client))
        t3 = asyncio.create_task(read_wifi(client))
        t4 = asyncio.create_task(read_esp_info())
        t5 = asyncio.create_task(publish_data(client))
        await asyncio.gather(t1, t2, t3, t4, t5)
    except OSError as e:
        dprint(f"Connection failed: {str(e)}.")
        return


try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()

