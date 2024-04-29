from machine import unique_id, Pin, I2C
from i2c_lcd import I2CLcd
import wifi_manager
import web_server
import config_manager
import time

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
lcd = I2CLcd(i2c)

# Mode Definitions
MODE_AP = 0
MODE_SHOW_IP = 1
MODE_SHOW_PRICE = 2

# Initialize global variables
current_mode = MODE_AP  # Start with AP Mode
last_price = ""
last_code = ""
last_button_press = time.ticks_ms()  # Initialize last button press time

# Initialize button
button = Pin(0, Pin.IN, Pin.PULL_UP)  # D3 on NodeMCU


def button_pressed(pin):
    global current_mode, last_button_press
    current_time = time.ticks_ms()
    if (current_time - last_button_press) < 200:  # 200 ms debounce period
        return  # Ignore this button press due to debounce
    last_button_press = current_time
    current_mode = (current_mode + 1) % 3  # Cycle through modes 0, 1, 2
    update_display()


def update_display():
    lcd.clear()  # Clear the display first to ensure it is clean
    if current_mode == MODE_AP:
        wifi_manager.setup_ap_mode()
    elif current_mode == MODE_SHOW_IP:
        ip, mac = wifi_manager.get_ip(), wifi_manager.get_mac()
        mac = mac.replace(':', '')  # Remove colons to save space
        lcd.lcd_string(f"{ip}", I2CLcd.LCD_LINE_1)
        lcd.lcd_string(f"{mac}", I2CLcd.LCD_LINE_2)
    elif current_mode == MODE_SHOW_PRICE:
        if last_price and last_code:
            lcd.lcd_string(f"{last_price}", I2CLcd.LCD_LINE_1)
            lcd.lcd_string(f"{last_code}", I2CLcd.LCD_LINE_2)
        else:
            lcd.lcd_string("No Price/Code Set", I2CLcd.LCD_LINE_1)


def run():
    global last_price, last_code, current_mode
    config_data = config_manager.read_config()
    last_price = config_data.get('last_price', '')
    last_code = config_data.get('last_code', '')

    if not wifi_manager.is_configured(config_data):
        print('Wifi not configured')
        current_mode = MODE_AP
        wifi_manager.setup_ap_mode()
    else:
        ssid = config_data.get('ssid', '')
        password = config_data.get('password', '')
        print("ssid", ssid, "Password" ,password)
        if wifi_manager.connect_wifi(ssid, password):
            ip = wifi_manager.get_ip()
            mac = wifi_manager.get_mac()
            web_server.notify_server(mac, ip)  # Call notify_server here after successful WiFi connection
            if last_price and last_code:
                current_mode = MODE_SHOW_PRICE
            else:
                current_mode = MODE_SHOW_IP
        else:
            print('Wifi could not get connected')
            current_mode = MODE_AP
            wifi_manager.setup_ap_mode()
    update_display()
    web_server.start()


button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)  # Interrupt on falling edge (button press)

if __name__ == '__main__':
    run()

