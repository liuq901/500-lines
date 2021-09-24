from cluster import *

from . import utils

class TestAcceptor(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.ac = Acceptor(self.node)

    def assertState(self, ballot_num, accepted_proposals):
        self.assertEqual(self.ac.ballot_num, ballot_num)
        self.assertEqual(self.ac.accepted_proposals, accepted_proposals)

    def test_prepare_new_ballot(self):
        proposal = Proposal('cli', 123, 'INC')
        self.ac.accepted_proposals = {33: (Ballot(19, 19), proposal)}
        self.ac.ballot_num = Ballot(10, 10)
        self.node.fake_message(Prepare(ballot_num=Ballot(19, 19)), sender='SC')
        self.assertMessage(['F999'], Accepting(leader='SC'))
        accepted_proposals = {33: (Ballot(19, 19), proposal)}
        self.verifyAcceptedProposals(accepted_proposals)
        self.assertMessage(['SC'], Promise(ballot_num=Ballot(19, 19), accepted_proposals=accepted_proposals))
        self.assertState(Ballot(19, 19), {33: (Ballot(19, 19), proposal)})

    def test_prepare_old_ballot(self):
        self.ac.ballot_num = Ballot(10, 10)
        self.node.fake_message(Prepare(ballot_num=Ballot(5, 10)), sender='SC')
        accepted_proposals = {}
        self.verifyAcceptedProposals(accepted_proposals)
        self.assertMessage(['SC'], Promise(ballot_num=Ballot(10, 10), accepted_proposals=accepted_proposals))
        self.assertState(Ballot(10, 10), {})

    def test_accept_new_ballot(self):
        proposal = Proposal('cli', 123, 'INC')
        self.ac.ballot_num = Ballot(10, 10)
        self.node.fake_message(Accept(slot=33, ballot_num=Ballot(19, 19), proposal=proposal), sender='CMD')
        self.assertMessage(['CMD'], Accepted(slot=33, ballot_num=Ballot(19, 19)))
        self.assertState(Ballot(19, 19), {33: (Ballot(19, 19), proposal)})

    def test_accepted_old_ballot(self):
        proposal = Proposal('cli', 123, 'INC')
        self.ac.ballot_num = Ballot(10, 10)
        self.node.fake_message(Accept(slot=33, ballot_num=Ballot(5, 5), proposal=proposal), sender='CMD')
        self.assertMessage(['CMD'], Accepted(slot=33, ballot_num=Ballot(10, 10)))
        self.assertState(Ballot(10, 10), {})
