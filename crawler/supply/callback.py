from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
import socket

selector = DefaultSelector()
stopped = False

class Fetcher(object):
    def __init__(self, url):
        self.response = b''
        self.url = url
        self.sock = None

    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect(('xkcd.com', 80))
        except BlockingIOError:
            pass

        selector.register(self.sock.fileno(), EVENT_WRITE, self.connected)

    def connected(self, key, mask):
        selector.unregister(key.fd)
        request = f'GET {self.url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
        self.sock.send(request.encode())

        selector.register(key.fd, EVENT_READ, self.read_response)

    def read_response(self, key, mask):
        global stopped

        self.response = self.sock.recv(4096)
        selector.unregister(key.fd)
        stopped = True

def fetch(url):
    fetcher = Fetcher(url)
    fetcher.fetch()

    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

    print(fetcher.response.decode())

if __name__ == '__main__':
    fetch('/26')
