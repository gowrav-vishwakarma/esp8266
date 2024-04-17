# main.py
import wifi_manager
import web_server
import config_manager
from machine import unique_id

def run():
    config_data = config_manager.read_config()
    if not wifi_manager.is_configured(config_data):
        wifi_manager.setup_ap_mode()
    else:
        if not wifi_manager.connect_wifi(config_data['ssid'], config_data['password']):
            wifi_manager.setup_ap_mode()

    # Notify a server with MAC and IP
    if wifi_manager.is_connected():
        web_server.notify_server(unique_id(), wifi_manager.get_ip())

    # Start the web server
    web_server.start()

if __name__ == '__main__':
    run()
