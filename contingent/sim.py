import hashlib
import os
import time

from contingent.projectlib import Project

import make

PATH = 'example'

def get_sources():
    res = []
    for file_name in os.listdir(PATH):
        name, ext = os.path.splitext(file_name)
        if ext == '.txt':
            res.append(file_name)
    return res

def get_md5(file_name):
    with open(os.path.join(PATH, file_name), 'rb') as fin:
        md5 = hashlib.md5()
        md5.update(fin.read())
        return md5.digest()

def file_changed(signature):
    res = []
    for file_name in signature:
        md5 = get_md5(file_name)
        if signature[file_name] != md5:
            signature[file_name] = md5
            res.append(file_name)
    return res

def main():
    make.set_dir(PATH)
    sources = get_sources()
    signature = {}
    for file_name in sources:
        make.output(file_name)
        signature[file_name] = get_md5(file_name)

    while True:
        changed_file = file_changed(signature)
        if changed_file:
            for file_name in changed_file:
                print(f'{file_name} changed')
                with make.project.cache_off():
                    make.change(file_name)
            make.project.start_tracing()
            make.project.rebuild()
            print(make.project.stop_tracing())
            print()
        time.sleep(1)

if __name__ == '__main__':
    main()
