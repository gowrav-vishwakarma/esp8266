# main.py
from machine import unique_id, Pin, I2C
from i2c_lcd import I2CLcd
import wifi_manager
import web_server
import config_manager

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
lcd = I2CLcd(i2c)

def run():
    config_data = config_manager.read_config()
    print("Configuration Data:", config_data)  # To debug and verify the correct parsing

    if not wifi_manager.is_configured(config_data):
        print("Wi-Fi not configured. Setting up AP mode...")
        wifi_manager.setup_ap_mode()
    else:
        ssid = config_data.get('ssid')
        password = config_data.get('password')
        if not wifi_manager.connect_wifi(ssid, password):
            print("Wi-Fi connection failed. Reverting to AP mode...")
            wifi_manager.setup_ap_mode()

    if wifi_manager.is_connected():
        ip = wifi_manager.get_ip()
        print(f"Connected with IP: {ip}")
        web_server.notify_server(unique_id(), ip)

    web_server.start()

if __name__ == '__main__':
    run()


if __name__ == '__main__':
    run()
