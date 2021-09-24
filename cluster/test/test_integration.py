import itertools
import unittest

from cluster import *

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.network = Network(1234)
        self.address = (f'node-{d}' for d in itertools.count())
        self.nodes = []
        self.events = []

    def tearDown(self):
        if self.events:
            self.fail(f'unhandled events: {self.events}')

    def event(self, name):
        self.events.append((self.network.now, name))

    def addNode(self, address):
        node = self.network.new_node(address=address)
        self.nodes.append(node)
        return node

    def assertEvent(self, time, name, fuzz=0):
        for i, e in enumerate(self.events):
            if e[1] == name and time - fuzz <= e[0] <= time + fuzz:
                self.events.pop(i)
                return
        self.fail(f'event {name} not found at or around time {time}; events: {self.events}')

    def setupNetwork(self, count, execute_fn=None):
        def add(state, input):
            state += input
            return state, state

        execute_fn = execute_fn or add
        peers = [f'N{n}' for n in range(count)]
        nodes = [self.addNode(p) for p in peers]
        Seed(nodes[0], initial_state=0, peers=peers, execute_fn=execute_fn)

        for node in nodes[1:]:
            bs = Bootstrap(node, execute_fn=execute_fn, peers=peers)
            bs.start()
        return nodes

    def kill(self, node):
        node.logger.info('KILLED BY TESTS')
        del self.network.nodes[node.address]

    def test_two_requests(self):
        nodes = self.setupNetwork(5)
        
        def request_done(output):
            self.event(f'request done: {output}')

        def make_request(n, node):
            self.event(f'request: {n}')
            req = Requester(node, n, request_done)
            req.start()

        for time, callback in [
            (1.0, lambda: make_request(5, nodes[1])),
            (5.0, lambda: make_request(6, nodes[2])),
            (10.0, self.network.stop),
        ]:
            self.network.set_timer(None, time, callback)

        self.network.run()
        self.assertEvent(1001.0, 'request: 5')
        self.assertEvent(1002.0, 'request done: 5', fuzz=1)
        self.assertEvent(1005.0, 'request: 6',)
        self.assertEvent(1006.0, 'request done: 11', fuzz=1)

    def test_parellel_requests(self):
        N = 10
        nodes = self.setupNetwork(5)
        results = []
        for n in range(1, N + 1):
            req = Requester(nodes[n % 4], n, results.append)
            self.network.set_timer(None, 1.0, req.start)

        self.network.set_timer(None, 10.0, self.network.stop)
        self.network.run()
        self.assertEqual((len(results), results and max(results)), (N, N * (N + 1) // 2), f'got {results}')

    def test_failed_nodes(self):
        N = 10
        nodes = self.setupNetwork(7)
        results = []
        for n in range(1, N + 1):
            req = Requester(nodes[n % 3], n, results.append)
            self.network.set_timer(None, n + 1, req.start)

        self.network.set_timer(None, N / 2 - 1, lambda: self.kill(nodes[3]))
        self.network.set_timer(None, N / 2, lambda: self.kill(nodes[4]))

        self.network.set_timer(None, N * 3.0, self.network.stop)
        self.network.run()
        self.assertEqual((len(results), results and max(results)), (N, N * (N + 1) // 2), f'got {results}')

    def test_failed_leader(self):
        N = 10

        def identity(state, input):
            return state, input

        nodes = self.setupNetwork(7, execute_fn=identity)
        results = []
        for n in range(1, N + 1):
            req = Requester(nodes[n % 6], n, results.append)
            self.network.set_timer(None, n + 1, req.start)

        def is_leader(n):
            try:
                leader_role = [c for c in n.roles if isinstance(c, Leader)][0]
                return leader_role.active
            except IndexError:
                return False

        def kill_leader():
            active_leader_nodes = [n for n in nodes if is_leader(n)]
            if active_leader_nodes:
                active_leader = active_leader_nodes[0]
                active_idx = nodes.index(active_leader)
                for n in range(1, N + 1):
                    if n % 6 == active_idx:
                        results.append(n)
                self.kill(active_leader)

        self.network.set_timer(None, n / 2, kill_leader)

        self.network.set_timer(None, 15, self.network.stop)
        self.network.run()
        self.assertEqual(set(results), set(range(1, N + 1)))
