import sys
import subprocess

def run_or_fail(*args):
    explanation = args[0]
    args = args[1:]
    try:
        res = subprocess.run(list(args), check=True, capture_output=True, shell=True)
    except subprocess.CalledProcessError:
        print(explanation, file=sys.stderr)
        sys.exit(1)
    return res.stdout
