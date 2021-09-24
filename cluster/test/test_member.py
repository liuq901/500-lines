import unittest
from unittest import mock

from cluster import *

from . import fake_network

class FakeRequest(object):
    def __init__(self, node, input_value, callback):
        self.node = node
        self.input_value = input_value
        self.callback = callback

    def start(self):
        self.callback(('ROTATED', self.node, self.input_value))

class TestMember(unittest.TestCase):
    def setUp(self):
        self.Node = mock.Mock(spec_set=Node)
        self.Bootstrap = mock.Mock(spec_set=Bootstrap)
        self.Seed = mock.Mock(spec_set=Seed)
        self.network = fake_network.FakeNetwork()
        self.state_machine = mock.Mock(name='state_machine')
        self.cls_args = {'bootstrap_cls': self.Bootstrap, 'seed_cls': self.Seed}

    def test_no_seed(self):
        sh = Member(self.state_machine, network=self.network, peers=['p1', 'p2'], **self.cls_args)
        self.assertFalse(self.Seed.called)
        self.Bootstrap.assert_called_with(self.network.node, execute_fn=self.state_machine, peers=['p1', 'p2'])

    def test_seed(self):
        sh = Member(self.state_machine, network=self.network, peers=['p1', 'p2'], seed=44, **self.cls_args)
        self.assertFalse(self.Bootstrap.called)
        self.Seed.assert_called_with(self.network.node, initial_state=44, peers=['p1', 'p2'], execute_fn=self.state_machine)

    def test_start(self):
        sh = Member(self.state_machine, network=self.network, peers=['p1', 'p2'], **self.cls_args)
        sh.start()
        sh.thread.join()
        sh.startup_role.start.assert_called_once_with()
        self.assertTrue(self.network.ran)

    def test_invoke(self):
        sh = Member(self.state_machine, network=self.network, peers=['p1', 'p2'], **self.cls_args)
        res = sh.invoke('ROTATE', request_cls=FakeRequest)
        self.assertEqual(sh.requester, None)
        self.assertEqual(res, ('ROTATED', sh.node, 'ROTATE'))
