# web_server.py
import socket
from config_manager import read_config, write_config
from lcd_setup import lcd, i2c
from i2c_lcd import I2CLcd


def start():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024)
        request = str(request)
        path = request.split(' ')[1]
        response=""

        if path.startswith('/config'):
            response = config_form()
        elif path.startswith('/saveconfig'):
            write_config(extract_config(request))
            response = 'Config saved! Reboot device.'
        elif path.startswith('/price'):
            response = display_price(request)

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + response)
        cl.close()

def config_form():
    return '<form action="/saveconfig"><input name="ssid"><input name="password"><input type="submit"></form>'

def extract_config(request):
    # Finds the start of the query string and extracts it
    start = request.find('?') + 1
    end = request.find(' ', start)
    query = request[start:end]

    # Parse the query string manually
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            key, value = key_value
            params[key] = unquote_plus(value)

    return params

def unquote_plus(string):
    # Replaces '+' with ' ' and decodes URL-encoded % escapes
    string = string.replace('+', ' ')
    parts = string.split('%')
    if len(parts) == 1:
        return string
    string = parts[0]
    for item in parts[1:]:
        try:
            string += chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            string += '%' + item
    return string

def display_price(request):
    # Extract query parameters
    start = request.find('?') + 1
    end = request.find(' ', start)
    query = request[start:end]
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            key, value = key_value
            params[key] = unquote_plus(value)

    # Extract specific price information
    mrp = params.get('mrp', 'N/A')
    sale_price = params.get('sale_price', 'N/A')
    code = params.get('code', 'N/A')

    # Create price information string
    price_info = f"{mrp}/- => {sale_price}/-"
    code_info = f"Code: {code}"

    # Display on LCD
    lcd.lcd_string(price_info, I2CLcd.LCD_LINE_1)
    lcd.lcd_string(code_info, I2CLcd.LCD_LINE_2)


    print(price_info)  # Optionally log this to the console or display on an LCD
    return price_info


def notify_server(mac, ip):
    print("MAC: {}, IP: {}".format(mac, ip))  # This would be an HTTP request in a real scenario

