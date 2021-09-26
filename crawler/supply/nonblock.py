import socket

def func(f, args, error, once=False):
    while True:
        try:
            return f(*args)
        except error:
            pass
        if once:
            break

def fetch(url):
    sock = socket.socket()
    sock.setblocking(False)
    func(sock.connect, (('xkcd.com', 80),), BlockingIOError, once=True)
    request = f'GET {url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
    func(sock.send, (request.encode(),), OSError)
    response = func(sock.recv, (4096,), BlockingIOError)
    print(response.decode())

if __name__ == '__main__':
    fetch('/26')

