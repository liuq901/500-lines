from collections import defaultdict

class Graph(object):
    sort_key = None

    def __init__(self):
        self._inputs_of = defaultdict(set)
        self._consequences_of = defaultdict(set)

    def sorted(self, nodes, reverse=False):
        nodes = list(nodes)
        try:
            nodes.sort(key=self.sort_key, reverse=reverse)
        except TypeError:
            pass
        return nodes

    def add_edge(self, input_task, consequence_task):
        self._consequences_of[input_task].add(consequence_task)
        self._inputs_of[consequence_task].add(input_task)

    def remove_edge(self, input_task, consequence_task):
        self._consequences_of[input_task].remove(consequence_task)
        self._inputs_of[consequence_task].remove(input_task)

    def inputs_of(self, task):
        return self.sorted(self._inputs_of[task])

    def clear_inputs_of(self, task):
        input_tasks = self._inputs_of.pop(task, ())
        for input_task in input_tasks:
            self._consequences_of[input_task].remove(task)

    def tasks(self):
        return self.sorted(set(self._inputs_of).union(self._consequences_of))

    def edges(self):
        return [(a, b) 
            for a in self.sorted(self._consequences_of)
            for b in self.sorted(self._consequences_of[a])]

    def immediate_consequences_of(self, task):
        return self.sorted(self._consequences_of[task])

    def recursive_consequences_of(self, tasks, include=False):
        def visit(task):
            visited.add(task)
            consequences = self._consequences_of[task]
            for consequence in self.sorted(consequences, reverse=True):
                if consequence not in visited:
                    yield from visit(consequence)
                    yield consequence

        def generate_consequences_backwards():
            for task in self.sorted(tasks, reverse=True):
                yield from visit(task)
                if include:
                    yield task

        visited = set()
        return list(generate_consequences_backwards())[::-1]
