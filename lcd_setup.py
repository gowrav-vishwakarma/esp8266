# lcd_setup.py
from machine import I2C, Pin
from i2c_lcd import I2CLcd

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
lcd = I2CLcd(i2c)

