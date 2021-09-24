from unittest import mock

from cluster import *

from . import utils

PROPOSAL1 = Proposal(caller='test', client_id=111, input='one')
PROPOSAL2 = Proposal(caller='test', client_id=222, input='two')
PROPOSAL3 = Proposal(caller='cli', client_id=127, input='tre')

class TestScout(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.sct = Scout(self.node, Ballot(10, 10), peers=['p1', 'p2', 'p3'])

    @mock.patch.object(Scout, 'send_prepare')
    def test_start(self, send_prepare):
        self.sct.start()
        send_prepare.assert_called_once_with()

    def test_send_prepare(self):
        self.sct.send_prepare()
        self.assertMessage(['p1', 'p2', 'p3'], Prepare(ballot_num=Ballot(10, 10)))
        self.assertNoMessages()
        self.network.tick(PREPARE_RETRANSMIT)
        self.assertMessage(['p1', 'p2', 'p3'], Prepare(ballot_num=Ballot(10, 10)))

    def test_PROMISE(self):
        self.sct.send_prepare()
        self.assertMessage(['p1', 'p2', 'p3'], Prepare(ballot_num=Ballot(10, 10)))
        for acceptor in 'p1', 'p3':
            accepted_proposals = {
                'p1': {1: (Ballot(5, 5), PROPOSAL1), 2: (Ballot(6, 6), PROPOSAL2)},
                'p3': {1: (Ballot(5, 99), PROPOSAL1), 2: (Ballot(6, 99), PROPOSAL2)},
            }[acceptor]
            self.verifyAcceptedProposals(accepted_proposals)
            self.node.fake_message(Promise(ballot_num=Ballot(10, 10), accepted_proposals=accepted_proposals), sender=acceptor)
        self.assertMessage(['F999'], Adopted(ballot_num=Ballot(10, 10), accepted_proposals={1: PROPOSAL1, 2: PROPOSAL2}))
        self.assertUnregistered()

    def test_PROMISE_preempted(self):
        self.sct.send_prepare()
        self.assertMessage(['p1', 'p2', 'p3'], Prepare(ballot_num=Ballot(10, 10)))
        accepted_proposals = {}
        self.verifyAcceptedProposals(accepted_proposals)
        self.node.fake_message(Promise(ballot_num=Ballot(99, 99), accepted_proposals=accepted_proposals), sender='p2')
        self.assertMessage(['F999'], Preempted(slot=None, preempted_by=Ballot(99, 99)))

    def test_update_accepted_empty(self):
        self.sct.update_accepted({})
        self.assertEqual(self.sct.accepted_proposals, {})

    def test_update_accepted_no_overlaps(self):
        self.sct.accepted_proposals[9] = (Ballot(9, 9), PROPOSAL1)
        self.sct.update_accepted({
            10: (Ballot(10, 10), PROPOSAL2),
            11: (Ballot(10, 10), PROPOSAL3),
        })
        self.assertEqual(self.sct.accepted_proposals, {
            9: (Ballot(9, 9), PROPOSAL1),
            10: (Ballot(10, 10), PROPOSAL2),
            11: (Ballot(10, 10), PROPOSAL3),
        })

    def test_update_accepted_highest_ballot_wins(self):
        self.sct.accepted_proposals[9] = (Ballot(9, 1), PROPOSAL1)
        self.sct.accepted_proposals[10] = (Ballot(10, 99), PROPOSAL1)
        self.sct.update_accepted({
            9: (Ballot(9, 99), PROPOSAL2),
            10: (Ballot(10, 1), PROPOSAL3),
        })
        self.assertEqual(self.sct.accepted_proposals, {
            9: (Ballot(9, 99), PROPOSAL2),
            10: (Ballot(10, 99), PROPOSAL1),
        })
