import os

from contingent.projectlib import Project

import make

path = 'example'

def get_sources(path):
    res = []
    for file_name in os.listdir(path):
        name, ext = os.path.splitext(file_name)
        if ext == '.txt':
            res.append(file_name)
    return res

def main():
    make.set_dir(path)
    sources = get_sources(path)

    for file_ in sources:
        make.output(file_)

if __name__ == '__main__':
    main()
