import argparse
import re
import socket
import socketserver
import subprocess
import time
import threading
import unittest

import helpers

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    dispatcher_server = None
    last_communication = None
    busy = False
    dead = False

class TestHandler(socketserver.BaseRequestHandler):
    command_re = re.compile(r'(\w+)(:.+)*')

    def send(self, data):
        self.request.sendall(data.encode())

    def recv(self, buf_size):
        return self.request.recv(buf_size).decode()

    def handle(self):
        self.data = self.recv(1024).strip()
        command_groups = self.command_re.match(self.data)
        command = command_groups.group(1)
        if not command:
            self.send('Invalid command')
            return
        if command == 'ping':
            print('pinged')
            self.server.last_communication = time.time()
            self.send('pong')
        elif command == 'runtest':
            print(f'got runtest command: am I busy? {self.server.busy}')
            if self.server.busy:
                self.send('BUSY')
            else:
                self.send('OK')
                print('running')
                commit_id = command_groups.group(2)[1:]
                self.server.busy = True
                self.run_tests(commit_id, self.server.repo_folder)
                self.server.busy = False
        else:
            self.send('Invalid command')

    def run_tests(self, commit_id, repo_folder):
        output = subprocess.run(['sh', 'test_runner_script.sh', repo_folder, commit_id], 
            check=True, capture_output=True, shell=True)
        print(output)
        test_folder = repo_folder
        suite = unittest.TestLoader().discover(test_folder)
        result_file = open('results', 'w')
        unittest.TextTestRunner(result_file).run(suite)
        result_file.close()
        result_file = open('results', 'r')
        output = result_file.read()
        helpers.communicate(self.server.dispatcher_server['host'],
            int(self.server.dispatcher_server['port']),
            f'results:{commit_id}:{len(output)}:{output}')

def serve():
    range_start = 8900
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='runner\'s host, by default it uses localhost',
        default='localhost', action='store')
    parser.add_argument('--port', help=f'runner\'s port, by default is uses values >= {range_start}',
        action='store')
    parser.add_argument('--dispatcher-server', help='dispatcher host:port, by default is uses localhost:8888',
        default='localhost:8888', action='store')
    parser.add_argument('repo', metavar='REPO', type=str, help='path to the repository this will observe')
    args = parser.parse_args()

    runner_host = args.host
    runner_port = None
    tries = 0
    if not args.port:
        runner_port = range_start
        while tries < 100:
            try:
                server = ThreadingTCPServer((runner_host, runner_port), TestHandler)
                print(server)
                print(runner_port)
                break
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    tries += 1
                    runner_port = range_start + tries
                    continue
                else:
                    raise e
        else:
            raise Exception(f'Could not bing to ports in range {range_start}-{range_start + tries}')
    else:
        runner_port = int(args.port)
        server = ThreadingTCPServer((runner_host, runner_port), TestHandler)
    server.repo_folder = args.repo

    dispatcher_host, dispatcher_port = args.dispatcher_server.split(':')
    server.dispatcher_server = {'host': dispatcher_host, 'port': dispatcher_port}
    response = helpers.communicate(server.dispatcher_server['host'], 
        int(server.dispatcher_server['port']),
        f'register:{runner_host}:{runner_port}')
    if response != 'OK':
        raise Exception('Can\'t register with dispatcher!')

    def dispatcher_checker(server):
        while not server.dead:
            time.sleep(5)
            if (time.time() - server.last_communication) > 10:
                try:
                    response = helpers.communicate(server.dispatcher_server['host'],
                        int(server.dispatcher_server['port']), 'status')
                    if response != 'OK':
                        print('Dispatcher is no longer functional')
                        server.shutdown()
                        return
                except socket.error as e:
                    print('Dispatcher is no longer functional')
                    server.shutdown()
                    return

    t = threading.Thread(target=dispatcher_checker, args=(server,))
    try:
        t.start()
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        server.dead = True
        t.join()
        server.shutdown()

if __name__ == '__main__':
    serve()
