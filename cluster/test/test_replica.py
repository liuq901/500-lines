from unittest import mock

from cluster import *

from . import utils

PROPOSAL1 = Proposal(caller='test', client_id=111, input='one')
PROPOSAL2 = Proposal(caller='test', client_id=222, input='two')
PROPOSAL3 = Proposal(caller='test', client_id=333, input='tre')
PROPOSAL4 = Proposal(caller='test', client_id=444, input='qua')

class TestReplica(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.execute_fn = mock.Mock(name='execute_fn', spec=lambda state, input: None)
        self.rep = Replica(self.node, self.execute_fn, state='state', slot=2, decisions={1: PROPOSAL1}, peers=['p1', 'F999'])
        self.assertNoMessages()

    def tearDown(self):
        self.assertNoMessages()

    @mock.patch.object(Replica, 'propose')
    def test_INVOKE_new(self, propose):
        self.node.fake_message(Invoke(
            caller=PROPOSAL2.caller, client_id=PROPOSAL2.client_id, 
            input_value=PROPOSAL2.input))
        propose.assert_called_with(PROPOSAL2, None)

    @mock.patch.object(Replica, 'propose')
    def test_INVOKE_repeat(self, propose):
        self.rep.proposals[1] = PROPOSAL1
        self.assertFalse(propose.called)

    def test_propose_new(self):
        self.rep.propose(PROPOSAL2)
        self.assertEqual(self.rep.next_slot, 3)
        self.assertMessage(['F999'], Propose(slot=2, proposal=PROPOSAL2))

    def test_propose_resend(self):
        self.rep.next_slot = 3
        self.rep.propose(PROPOSAL2, 2)
        self.assertEqual(self.rep.next_slot, 3)
        self.assertMessage(['F999'], Propose(slot=2, proposal=PROPOSAL2))

    @mock.patch.object(Replica, 'commit')
    def test_DECISION_gap(self, commit):
        self.node.fake_message(Decision(slot=3, proposal=PROPOSAL3))
        self.assertEqual(self.rep.next_slot, 4)
        self.assertEqual(self.rep.decisions[3], PROPOSAL3)
        self.assertFalse(commit.called)

    @mock.patch.object(Replica, 'commit')
    def test_DECISION_commit(self, commit):
        self.node.fake_message(Decision(slot=2, proposal=PROPOSAL2))
        self.assertEqual(self.rep.next_slot, 3)
        self.assertEqual(self.rep.decisions[2], PROPOSAL2)
        commit.assert_called_once_with(2, PROPOSAL2)

    @mock.patch.object(Replica, 'commit')
    def test_DECISION_commit_cascade(self, commit):
        self.node.fake_message(Decision(slot=3, proposal=PROPOSAL3))
        self.assertFalse(commit.called)
        self.node.fake_message(Decision(slot=2, proposal=PROPOSAL2))
        self.assertEqual(self.rep.next_slot, 4)
        self.assertEqual(self.rep.decisions[2], PROPOSAL2)
        self.assertEqual(self.rep.decisions[3], PROPOSAL3)
        self.assertEqual(commit.call_args_list, [
            mock.call(2, PROPOSAL2), mock.call(3, PROPOSAL3),
        ])

    @mock.patch.object(Replica, 'commit')
    def test_DECISION_repeat(self, commit):
        self.node.fake_message(Decision(slot=1, proposal=PROPOSAL1))
        self.assertEqual(self.rep.next_slot, 2)
        self.assertFalse(commit.called)

    @mock.patch.object(Replica, 'commit')
    def test_DECISION_repeat_conflict(self, commit):
        self.assertRaises(AssertionError, lambda: self.node.fake_message(Decision(slot=1, proposal=PROPOSAL2)))

    def test_join(self):
        self.node.fake_message(Join(), sender='F999')
        self.assertMessage(['F999'], Welcome(state='state', slot=2, decisions={1: PROPOSAL1}))

    def test_join_unknown(self):
        self.node.fake_message(Join(), sender='999')
        self.assertNoMessages()
