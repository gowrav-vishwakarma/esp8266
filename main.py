# main.py
from machine import unique_id, Pin, I2C
from i2c_lcd import I2CLcd
import wifi_manager
import web_server
import config_manager

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
lcd = I2CLcd(i2c)

# Mode Definitions
MODE_AP = 0
MODE_SHOW_IP = 1
MODE_SHOW_PRICE = 2

current_mode = MODE_AP  # Start with AP Mode

# Initialize button
button = Pin(0, Pin.IN, Pin.PULL_UP)  # D3 on NodeMCU

# Global state
current_mode = MODE_AP  # Start with AP Mode
last_price = ""

def button_pressed(pin):
    global current_mode
    current_mode = (current_mode + 1) % 3  # Cycle through modes 0, 1, 2
    update_display()

def update_display():
    global last_price
    if current_mode == MODE_AP:
        wifi_manager.setup_ap_mode()
    elif current_mode == MODE_SHOW_IP:
        ip, mac = wifi_manager.get_ip(), wifi_manager.get_mac()
        lcd.lcd_string(f"IP: {ip}", I2CLcd.LCD_LINE_1)
        lcd.lcd_string(f"MAC: {mac}", I2CLcd.LCD_LINE_2)
    elif current_mode == MODE_SHOW_PRICE:
        if last_price:
            lcd.lcd_string(f"Price: {last_price}", I2CLcd.LCD_LINE_1)
        else:
            lcd.lcd_string("No Price Set", I2CLcd.LCD_LINE_1)
    lcd.clear()

def run():
    global last_price
    config_data = config_manager.read_config()
    last_price = config_data.get('last_price', '')

    if not wifi_manager.is_configured(config_data):
        wifi_manager.setup_ap_mode()
    else:
        ssid = config_data['ssid']
        password = config_data['password']
        if not wifi_manager.connect_wifi(ssid, password):
            wifi_manager.setup_ap_mode()
        else:
            if last_price:
                current_mode = MODE_SHOW_PRICE
            else:
                current_mode = MODE_SHOW_IP
            update_display()

    web_server.start()

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)  # Interrupt on falling edge (button press)

if __name__ == '__main__':
    run()
