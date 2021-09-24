import unittest

from cluster import *

from . import fake_network

class ComponentTestCase(unittest.TestCase):
    def setUp(self):
        self.network = fake_network.FakeNetwork()
        self.node = fake_network.FakeNode(self.network)

    def tearDown(self):
        if self.node.sent:
            self.fail(f'extra messages from node : {self.node.sent}')

    def assertMessage(self, destinations, message):
        got = self.node.sent.pop(0)
        self.assertEqual((sorted(got[0]), got[1]), (sorted(destinations), message))

    def assertNoMessages(self):
        self.assertEqual(self.node.sent, [])

    def assertTimers(self, timers):
        self.assertEqual(self.node.network.get_timers(), timers)

    def assertUnregistered(self):
        self.assertEqual(self.node.roles, [])

    def verifyAcceptedProposals(self, accepted_proposals):
        self.assertIsInstance(accepted_proposals, dict)
        for k, v in accepted_proposals.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, tuple)
            self.assertEqual(len(v), 2)
            self.assertIsInstance(v[0], Ballot)
            self.assertIsInstance(v[1], Proposal)
