# web_server.py
import socket
from config_manager import read_config, write_config

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
    # Extracts SSID and password from the request
    lines = request.split('\r\n')
    body = lines[-1]  # Assuming the body content in the last line
    params = body.split('&')
    config = {param.split('=')[0]: param.split('=')[1] for param in params}
    return config

def display_price(request):
    # Logic to extract price data from the request and display it
    price_info = "MRP: $100, Sale Price: $80, Code: 12345"  # Mock data
    print(price_info)  # Display on console for now, later switch to LCD
    return price_info

def notify_server(mac, ip):
    print("MAC: {}, IP: {}".format(mac, ip))  # This would be an HTTP request in a real scenario
