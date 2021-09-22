import argparse
import os
import socket
import subprocess
import time

import helpers

def poll():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dispatcher-server',
        help='dispatcher host:port, by default it uses localhost:8888',
        default='localhost:8888',
        action='store')
    parser.add_argument('repo', metavar='REPO', type=str,
        help='path to the repository this will observe')
    args = parser.parse_args()
    dispatcher_host, dispatcher_port = args.dispatcher_server.split(':')
    while True:
        try:
            subprocess.run(['sh', 'update_repo.sh', args.repo], check=True, capture_output=True, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Could not update and check repository. Reason: {e.stderr.decode("gbk").strip()}')

        if os.path.isfile('.commit_id'):
            try:
                response = helpers.communicate(dispatcher_host, int(dispatcher_port), 'status')
            except socket.error as e:
                raise Exception(f'Could not communicate with dispatcher server: {e}')
            if response == 'OK':
                commit = ''
                with open('.commit_id', 'r') as f:
                    commit = f.readline()
                response = helpers.communicate(dispatcher_host, int(dispatcher_port), f'dispatch:{commit}')
                if response != 'OK':
                    raise Exception(f'Could not dispatch the test: {response}')
                print('dispatched!')
            else:
                raise Exception(f'Could not dispatcher the test: {response}')
        time.sleep(5)

if __name__ == '__main__':
    poll()
