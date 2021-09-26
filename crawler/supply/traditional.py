import socket

def fetch(url):
    sock = socket.socket()
    sock.settimeout(1)
    sock.connect(('xkcd.com', 80))
    request = f'GET {url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
    sock.send(request.encode())
    response = sock.recv(4096)
    print(response.decode())

if __name__ == '__main__':
    fetch('/26')
