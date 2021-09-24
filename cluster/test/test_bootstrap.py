from unittest import mock

from cluster import *

from . import utils

class TestBootstrap(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.cb_args = None
        self.execute_fn = mock.Mock()

        self.Replica = mock.Mock(spec_set=Replica)
        self.Acceptor = mock.Mock(spec_set=Acceptor)
        self.Leader = mock.Mock(spec_set=Leader)
        self.Commander = mock.Mock(spec_set=Commander)
        self.Scout = mock.Mock(spec_set=Scout)

        self.bs = Bootstrap(
            self.node, ['p1', 'p2', 'p3'], self.execute_fn,
            replica_cls=self.Replica, acceptor_cls=self.Acceptor,
            leader_cls=self.Leader, commander_cls=self.Commander,
            scout_cls=self.Scout,
        )

    def test_retransmit(self):
        self.bs.start()
        for recip in 'p1', 'p2', 'p3', 'p1':
            self.assertMessage([recip], Join())
            self.network.tick(JOIN_RETRANSMIT)
        self.assertMessage(['p2'], Join())

        self.node.fake_message(Welcome(state='st', slot='s1', decisions={}))
        self.Acceptor.assert_called_with(self.node)
        self.Replica.assert_called_with(self.node, execute_fn=self.execute_fn, decisions={},
            state='st', slot='s1', peers=['p1', 'p2', 'p3',])
        self.Leader.assert_called_with(self.node, peers=['p1', 'p2', 'p3'], 
            commander_cls=self.Commander, scout_cls=self.Scout)
        self.Leader().start.assert_called_with()
        self.assertTimers([])
        self.assertUnregistered()
