# wifi_manager.py
import network
from time import sleep

ap = network.WLAN(network.AP_IF)
sta = network.WLAN(network.STA_IF)

def is_configured(config):
    return 'ssid' in config and 'password' in config

def connect_wifi(ssid, password):
    sta.active(True)
    sta.connect(ssid, password)
    for _ in range(10):
        if sta.isconnected():
            return True
        sleep(1)
    return False

def setup_ap_mode():
    ap.active(True)
    ap.config(essid='ESP8266-AP', password='123456789')
    print('AP Mode: Connect to ESP8266-AP with IP:', ap.ifconfig()[0])

def is_connected():
    return sta.isconnected()

def get_ip():
    return sta.ifconfig()[0]
