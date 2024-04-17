# wifi_manager.py
import network
from time import sleep
from machine import unique_id, Pin, I2C
from i2c_lcd import I2CLcd
from lcd_setup import lcd, i2c


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
    lcd.lcd_string("ESP8266-AP", I2CLcd.LCD_LINE_1)
    lcd.lcd_string(ap.ifconfig()[0], I2CLcd.LCD_LINE_2)

def is_connected():
    return sta.isconnected()

def get_ip():
    return sta.ifconfig()[0]

