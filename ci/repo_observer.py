import argparse
import subprocess

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
            subprocess.run(['python', 'update_repo.py', args.repo], check=True, capture_output=True, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Could not update and check repository. Reason: {e.stderr.decode("gbk").strip()}')

if __name__ == '__main__':
    poll()
