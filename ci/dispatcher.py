import argparse
import re
import socket
import socketserver
import time
import threading

import helpers

def dispatch_tests(server, commit_id):
    while True:
        print('trying to dispatch to runners')
        for runner in server.runners:
            response = helpers.communicate(runner['host'], int(runner['port']), f'runtest:{commit_id}')
            if response == 'OK':
                print(f'adding id {commit_id}')
                server.dispatched_commits[commit_id] = runner
                if commit_id in server.pending_commits:
                    server.pending_commits.remove(commit_id)
                return
        time.sleep(2)

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    runners = []
    dead = False
    dispatched_commits = {}
    pending_commits = []

class DispatcherHandler(socketserver.BaseRequestHandler):
    command_re = re.compile(r'(\w+)(:.+)*')
    BUF_SIZE = 1024

    def send(self, data):
        self.request.sendall(data.encode())

    def recv(self, buf_size):
        return self.request.recv(buf_size).decode()

    def handle(self):
        self.data = self.recv(self.BUF_SIZE).strip()
        command_groups = self.command_re.match(self.data)
        if not command_groups:
            self.send('Invalid command')
            return
        command = command_groups.group(1)
        if command == 'status':
            print('in status')
            self.send('OK')
        elif command == 'register':
            print('register')
            address = command_groups.group(2)
            host, port = re.findall(r':(\w*)', address)
            runner = {'host': host, 'port': port}
            self.server.runners.append(runner)
            self.send('OK')
        elif command == 'dispatch':
            print('going to dispatch')
            commit_id = command_groups.group(2)[1:]
            if not self.server.runners:
                self.send('No runners are registered')
            else:
                self.send('OK')
                dispatch_tests(self.server, commit_id)
        elif command == 'results':
            print('got test results')
            results = command_groups.group(2)[1:]
            results = results.split(':')
            commit_id = results[0]
            length_msg = int(results[1])
            remaining_buffer = self.BUF_SIZE - (len(command) + len(commit_id) + len(results[1]) + 3)
            if length_msg > remaining_buffer:
                self.data += self.recv(length_msg - remaining_buffer).strip()
            del self.server.dispatched_commits[commit_id]
            if not os.path.exists('test_results'):
                os.makedirs('test_results')
            with open(f'test_results/{commit_id}', 'w') as f:
                data = self.data.split(':')[3:]
                data = '\n'.join(data)
                f.write(data)
            self.send('OK')
        else:
            self.send('Invalid command')

def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='dispatcher\'s host, by default it uses localhost',
        default='localhost', action='store')
    parser.add_argument('--port', help='dispatcher\'s port, by default it uses 8888',
        default=8888, action='store')
    args = parser.parse_args()

    server = ThreadingTCPServer((args.host, int(args.port)), DispatcherHandler)
    print(f'serving on {args.host}:{args.port}')

    def runner_checker(server):
        def manage_commit_lists(runner):
            for commit, assigned_runner in server.dispatched_commits.items():
                if assigned_runner == runner:
                    del server.dispatched_commits[commit]
                    server.pending_commits.append(commit)
                    break
            server.runners.remove(runner)

        while not server.dead:
            time.sleep(1)
            for runner in server.runners:
                try:
                    response = helpers.communicate(runner['host'], int(runner['port']), 'ping')
                    if response != 'pong':
                        print(f'removing runner {runner}')
                        manage_commit_lists(runner)
                except socket.error as e:
                    manage_commit_lists(runner)

    def redistribute(server):
        while not server.dead:
            for commit in server.pending_commits:
                print('running redistribute')
                print(commit)
                dispatch_tests(server, commit)
                time.sleep(5)

    runner_heartbeat = threading.Thread(target=runner_checker, args=(server,))
    redistributor = threading.Thread(target=redistribute, args=(server,))
    try:
        runner_heartbeat.start()
        redistributor.start()
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        server.dead = True
        runner_heartbeat.join()
        redistributor.join()

if __name__ == '__main__':
    serve()
