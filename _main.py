from machine import Pin, I2C
import time
from i2c_lcd import I2CLcd

def run():
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
    lcd = I2CLcd(i2c)
    led = Pin(2, Pin.OUT, value=1)
    error_occurred = False

    try:
        lcd.lcd_string("Hello World!", I2CLcd.LCD_LINE_1)
        lcd.lcd_string("MicroPython", I2CLcd.LCD_LINE_2)
    except Exception as e:
        print("Error during LCD operation:", str(e))
        error_occurred = True

    while True:
        led.value(not led.value())  # Toggle LED state
        if error_occurred:
            time.sleep(5)  # Slow blink rate if an error occurred
        else:
            time.sleep(1)  # Fast blink rate if no error occurred

if __name__ == '__main__':
    run()