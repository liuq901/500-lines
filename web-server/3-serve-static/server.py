import http.server
import os

class ServerException(Exception):
    pass

class RequestHandler(http.server.BaseHTTPRequestHandler):
    Error_Page = '\n'.join([
        '<html>', '<body>',
        '<h1>Error accessing {path}</h1>',
        '<p>{msg}</p>',
        '</body>', '</html>',
    ])

    def do_GET(self):
        try:
            full_path = os.getcwd() + '/3-serve-static' + self.path

            if not os.path.exists(full_path):
                raise ServerException(f'\'{self.path}\' not found.')
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            else:
                raise ServerException(f'Unknown object \'{self.path}\'')
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
