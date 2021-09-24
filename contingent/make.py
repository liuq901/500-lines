import os
import re

from contingent.projectlib import Project

LINK = '<a href="{}">{}</a>'
PAGE = '<h1>{}</h1>\n<p>\n{}\n</p>'
PATH = None

project = Project()
task = project.task

def set_dir(path):
    global PATH
    PATH = path

def change_ext(filename):
    name, ext = os.path.splitext(filename)
    return f'{name}.html'

@task
def read(path):
    with open(os.path.join(PATH, path), 'r') as f:
        return f.read()

@task
def parse(filename):
    lines = read(filename).strip().splitlines()
    title = lines[0]
    body = '\n'.join(lines[2:])
    return title, body

@task
def title_of(filename):
    title, body = parse(filename)
    return title

def make_link(match):
    filename = match.group(1)
    return LINK.format(change_ext(filename), title_of(filename))

@task
def render(filename):
    title, body = parse(filename)
    body = re.sub(r'`([^`]+)`', make_link, body.replace('\n', '<br>'))
    return PAGE.format(title, body)

@task
def output(filename):
    global PATH
    with open(os.path.join(PATH, change_ext(filename)), 'w') as f:
        f.write(render(filename))
