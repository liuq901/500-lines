import http.server
import os
from subprocess import PIPE
from subprocess import Popen

class ServerException(Exception):
    pass

class case_no_file(object):
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException(f'\'{handler.path}\' not found')

class case_cgi_file(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)

class case_existing_file(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)

class case_directory_index_file(object):
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(object):
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_always_fail(object):
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException(f'Unknown object \'{handler.path}\'')

class RequestHandler(http.server.BaseHTTPRequestHandler):
    Cases = [
        case_no_file(),
        case_cgi_file(),
        case_existing_file(),
        case_directory_index_file(),
        case_directory_no_index_file(),
        case_always_fail(),
    ]

    Error_Page = '\n'.join([
        '<html>', '<body>',
        '<h1>Error accessing {path}</h1>',
        '<p>{msg}</p>',
        '</body>', '</html>',
    ])

    Listing_Page = '\n'.join(['<html>', '<body>', '<ul>', '{0}', '</ul>', '</body>', '</html>'])

    def do_GET(self):
        try:
            self.full_path = os.getcwd() + '/5-cgi' + self.path

            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'r') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = f'\'{self.path}\' cannot be read: {msg}'
            self.handle_error(msg)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = [f'<li>{e}</li>' for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = f'\'{self.path}\' cannot be read: {msg}'
            self.handle_error(msg)

    def run_cgi(self, full_path):
        cmd = 'python ' + full_path
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
        child_stdin, child_stdout = p.stdin, p.stdout
        child_stdin.close()
        data = child_stdout.read().decode()
        child_stdout.close()
        self.send_content(data)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content.encode())

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
