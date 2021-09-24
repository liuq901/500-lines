from contextlib import contextmanager
from collections import namedtuple
from functools import wraps

from .graphlib import Graph

_unavailable = object()

class Project(object):
    def __init__(self):
        self._graph = Graph()
        self._graph.sort_key = task_key
        self._cache = {}
        self._cache_on = True
        self._task_stack = []
        self._todo = set()
        self._trace = None

    def start_tracing(self):
        self._trace = []

    def stop_tracing(self, verbose=False):
        text = '\n'.join(
            '{}{} {}'.format(
                '. ' * depth,
                'calling' if not_available else 'returning cached',
                task,
            ) for (depth, not_available, task) in self._trace if verbose or not_available
        )

        self._trace = None
        return text

    def _add_task_to_trace(self, task, return_value):
        tup = (len(self._task_stack), return_value is _unavailable, task)
        self._trace.append(tup)

    def task(self, task_function):
        @wraps(task_function)
        def wrapper(*args):
            task = Task(wrapper, args)

            if self._task_stack:
                self._graph.add_edge(task, self._task_stack[-1])

            return_value = self._get_from_cache(task)
            if self._trace is not None:
                self._add_task_to_trace(task, return_value)

            if return_value is _unavailable:
                self._graph.clear_inputs_of(task)
                self._task_stack.append(task)
                try:
                    return_value = task_function(*args)
                finally:
                    self._task_stack.pop()
                self.set(task, return_value)

            return return_value

        return wrapper

    def _get_from_cache(self, task):
        if not self._cache_on:
            return _unavailable
        if task in self._todo:
            return _unavailable
        return self._cache.get(task, _unavailable)

    @contextmanager
    def cache_off(self):
        original_value = self._cache_on
        self._cache_on = False
        try:
            yield
        finally:
            self._cache_on = original_value

    def set(self, task, return_value):
        self._todo.discard(task)
        if (task not in self._cache) or (self._cache[task] != return_value):
            self._cache[task] = return_value
            self._todo.update(self._graph.immediate_consequences_of(task))

    def invalidate(self, task):
        self._todo.add(task)

    def rebuild(self):
        while self._todo:
            tasks = self._graph.recursive_consequences_of(self._todo, True)
            for function, args in tasks:
                function(*args)

def task_key(task):
    function, args = task
    return function.__name__, args

class Task(namedtuple('Task', ('task_function', 'args'))):
    __slots__ = ()

    def __new__(cls, task_function, args):
        try:
            hash(args)
        except TypeError as e:
            raise ValueError(f'arguments to project tasks must be immutable and hashable, not the {e}')

        return super().__new__(cls, task_function, args)

    def __repr__(self):
        return f'{self.task_function.__name__}({", ".join(repr(arg) for arg in self.args)})'
