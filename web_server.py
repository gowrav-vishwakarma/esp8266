# web_server.py
import socket
from config_manager import read_config, write_config
from lcd_setup import lcd, i2c
from i2c_lcd import I2CLcd
import machine
import urequests as requests


def start():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    error_count = 0  # Initialize error counter

    while True:
        try:
            cl, addr = s.accept()
            print('Connection from', addr)
            try:
                request = cl.recv(1024)
                if not request:
                    print('No data received!')
                    lcd.lcd_string("No data received", I2CLcd.LCD_LINE_1)
                    cl.close()
                    continue

                request = str(request)
                path = request.split(' ')[1]
                response = ""

                if path.startswith('/config'):
                    response = config_form()
                elif path.startswith('/saveconfig'):
                    write_config(extract_config(request))
                    response = 'Config saved! Rebooting device...'
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + response)
                    cl.close()
                    machine.reset()
                elif path.startswith('/price'):
                    response = display_price(request)

                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + response)
            except Exception as e:
                print('Failed to handle request:', e)
                lcd.lcd_string("Error: See console", I2CLcd.LCD_LINE_1)
                error_count += 1
            finally:
                cl.close()
        except OSError as e:
            print('Network error:', e)
            lcd.lcd_string("Net error: Reboot?", I2CLcd.LCD_LINE_1)
            error_count += 1

        # Check if errors have reached a threshold
        if error_count >= 10:
            lcd.lcd_string("Many errors! Rebooting...", I2CLcd.LCD_LINE_1)
            machine.sleep(5000)  # Wait for 5 seconds before rebooting
            machine.reset()


def config_form():
    config = read_config()
    ssid = config.get('ssid', '')
    password = config.get('password', '')
    warehouse_id = config.get('warehouse_id', '')
    register_url = config.get('register_url', "http://default.url/register")

    return '''
    <form action="/saveconfig" method="get">
        SSID: <input name="ssid" type="text" placeholder="SSID" value="{ssid}"><br>
        Password: <input name="password" type="password" placeholder="Password" value="{password}"><br>
        Warehouse ID: <input name="warehouse_id" type="text" placeholder="Warehouse ID" value="{warehouse_id}"><br>
        Register URL: <input name="register_url" type="text" value="{register_url}"><br>
        <input type="submit" value="Save Configuration">
    </form>
    '''.format(ssid=ssid, password=password, warehouse_id=warehouse_id, register_url=register_url)

def extract_config(request):
    start = request.find('?') + 1
    end = request.find(' ', start)
    query = request[start:end]
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            key, value = key_value
            params[key] = unquote_plus(value)
    return params

def unquote_plus(string):
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
    start = request.find('?') + 1
    end = request.find(' ', start)
    query = request[start:end]
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            key, value = key_value
            params[key] = unquote_plus(value)

    mrp = params.get('mrp', 'N/A')
    sale_price = params.get('sale_price', 'N/A')
    code = params.get('code', 'N/A')

    price_info = f"{sale_price}/- ({mrp}/-)"
    code_info = f"{code}"

    # Save last price to config
    config = read_config()
    config['last_price'] = price_info
    config['last_code'] = code_info
    write_config(config)

    lcd.lcd_string(price_info, I2CLcd.LCD_LINE_1)
    lcd.lcd_string(code_info, I2CLcd.LCD_LINE_2)

    print(price_info)  # Optionally log this to the console or display on an LCD
    return price_info


def notify_server(mac, ip):
    config = read_config()
    warehouse_id = config.get('warehouse_id', 'default_warehouse_id')  # Provide a default warehouse_id
    register_url = config.get('register_url', "https://ahmedabad-wmsnest.service.staging.frendy.in/pos/registerdevice")

    # Clean up MAC address format by removing ':' if present
    mac = mac.replace(':', '')

    # Construct the URL with parameters
    url = f"{register_url}?warehouseId={warehouse_id}&macAddress={mac}&localIp={ip}"
    # url = f"https://google-translate1.p.rapidapi.com/language/translate/v2/languages?warehouseId={warehouse_id}&macAddress={mac}&localIp={ip}"
    print("Making HTTP GET request to:", url)

    headers = {
       'Host': "ahmedabad-wmsnest.service.staging.frendy.in",
       'User-Agent': 'ESP8266'
    }

    try:
        response = requests.get(url, headers=headers)
        print("HTTP Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Body:", response.text)
        if response.status_code == 200:
            print("Successfully registered device.")
            lcd.lcd_string("Device registered", I2CLcd.LCD_LINE_1)
        else:
            print("Failed to register device:", response.text)
            lcd.lcd_string("Registration failed", I2CLcd.LCD_LINE_1)
        response.close()  # It's important to close response objects to free up resources.
    except Exception as e:
        print("Error sending registration request:", e)
        lcd.lcd_string("HTTP request failed", I2CLcd.LCD_LINE_1)
