from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
import socket

selector = DefaultSelector()
stopped = False

class Future(object):
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

class Task(object):
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return

        next_future.add_done_callback(self.step)

def connect(sock):
    f = Future()

    def on_connected():
        f.set_result(None)

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield f
    selector.unregister(sock.fileno())

def read(sock):
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield f
    selector.unregister(sock.fileno())
    return chunk

class Fetcher(object):
    def __init__(self, url):
        self.response = b''
        self.url = url

    def fetch(self):
        global stopped

        sock = socket.socket()
        sock.setblocking(False)
        try:
            sock.connect(('xkcd.com', 80))
        except BlockingIOError:
            pass

        yield from connect(sock)

        request = f'GET {self.url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
        sock.send(request.encode())

        self.response = yield from read(sock)
        stopped = True

def fetch(url):
    fetcher = Fetcher(url)
    Task(fetcher.fetch())

    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

    print(fetcher.response.decode())

if __name__ == '__main__':
    fetch('/26')
