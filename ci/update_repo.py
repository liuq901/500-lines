import os
import sys

from run_or_fail import run_or_fail

def main():
    if os.path.exists('.commit_id'):
        os.remove('.commit_id')

    run_or_fail('Repository folder not found!', 'pushd', sys.argv[1])
    run_or_fail('Could not reset git', 'git', 'reset', '--hard', 'HEAD')

    commit = run_or_fail('Could not call \'git log\' on repository', 'git', 'log', '-n1').decode()
    commit_id = commit.split()[1]

    run_or_fail('Could not pull from repository', 'git', 'pull')

    commit = run_or_fail('Could not call \'git log\' on repository', 'git', 'log', '-n1').decode()
    new_commit_id = commit.split()[1]

    if commit_id != new_commit_id:
        with open('.commit_id', 'w') as out_file:
            out_file.write(new_commit_id)

if __name__ == '__main__':
    main()
