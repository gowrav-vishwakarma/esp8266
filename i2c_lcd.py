import time


class I2CLcd:
    LCD_I2C_ADDR = 0x27
    LCD_WIDTH = 16
    LCD_CHR = 1
    LCD_CMD = 0
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00
    ENABLE = 0b00000100
    E_PULSE = 0.001  # Increase to 1ms
    E_DELAY = 0.005  # Increase to 5ms

    def __init__(self, i2c, address=None):
        self.i2c = i2c
        self.address = address if address else self.LCD_I2C_ADDR
        try:
            self.init_lcd()
        except Exception as e:
            print("Initialization error:", str(e))

    def init_lcd(self):
        commands = [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]
        try:
            for cmd in commands:
                self.lcd_byte(cmd, self.LCD_CMD)
            time.sleep(self.E_DELAY)
        except Exception as e:
            print("LCD command error:", str(e))

    def lcd_byte(self, bits, mode):
        try:
            bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
            bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT
            self.i2c.writeto(self.address, bytearray([bits_high, bits_high | self.ENABLE, bits_high]))
            time.sleep(self.E_PULSE)
            self.i2c.writeto(self.address, bytearray([bits_high, bits_high & ~self.ENABLE, bits_high]))
            time.sleep(self.E_DELAY)
            self.i2c.writeto(self.address, bytearray([bits_low, bits_low | self.ENABLE, bits_low]))
            time.sleep(self.E_PULSE)
            self.i2c.writeto(self.address, bytearray([bits_low, bits_low & ~self.ENABLE, bits_low]))
            time.sleep(self.E_DELAY)
        except Exception as e:
            print("Byte transmission error:", str(e))

    def lcd_string(self, message, line):
        try:
            def custom_ljust(s, width, fillchar=' '):
                """Implements a simple left-justify similar to str.ljust()."""
                return s + fillchar * (width - len(s))

            message = custom_ljust(message, self.LCD_WIDTH, ' ')
            self.lcd_byte(line, self.LCD_CMD)
            for char in message:
                self.lcd_byte(ord(char), self.LCD_CHR)
        except Exception as e:
            print("String display error:", str(e))

    def clear(self):
        try:
            self.lcd_byte(0x01, self.LCD_CMD)
            time.sleep(self.E_DELAY)
        except Exception as e:
            print("Clear display error:", str(e))

