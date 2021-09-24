from unittest import mock

from cluster import *

from . import utils

class TestSeed(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.Bootstrap = mock.Mock(spec_set=Bootstrap)
        self.execute_fn = mock.Mock()
        self.seed = Seed(self.node, initial_state='state', peers=['p1', 'p2', 'p3'],
            execute_fn=self.execute_fn, bootstrap_cls=self.Bootstrap)

    def test_JOIN(self):
        self.node.fake_message(Join(), sender='p1')
        self.assertNoMessages()
        self.node.fake_message(Join(), sender='p3')
        self.assertMessage(['p1', 'p3'], Welcome(state='state', slot=1, decisions={}))
        self.network.tick(JOIN_RETRANSMIT)
        self.node.fake_message(Join(), sender='p2')
        self.assertMessage(['p1', 'p2', 'p3'], Welcome(state='state', slot=1, decisions={}))
        self.network.tick(JOIN_RETRANSMIT * 2)
        self.assertNoMessages()
        self.assertUnregistered()
        self.Bootstrap.assert_called_with(self.node, peers=['p1', 'p2', 'p3'], execute_fn=self.execute_fn)
        self.Bootstrap().start.assert_called_with()
