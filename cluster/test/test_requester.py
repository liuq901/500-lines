from unittest import mock

from cluster import *

from . import utils

CLIENT_ID = 999999

class TestRequester(utils.ComponentTestCase):
    def setUp(self):
        super().setUp()
        self.callback = mock.Mock(name='callback')
        with mock.patch.object(Requester, 'cliend_ids') as cliend_ids:
            cliend_ids.__next__.return_value = CLIENT_ID
            self.req = Requester(self.node, 10, self.callback)
        self.assertEqual(self.req.client_id, CLIENT_ID)

    def test_function(self):
        self.req.start()
        self.assertMessage(['F999'], Invoke(caller='F999', client_id=CLIENT_ID, input_value=10))
        self.network.tick(INVOKE_RETRANSMIT)
        self.assertMessage(['F999'], Invoke(caller='F999', client_id=CLIENT_ID, input_value=10))
        self.node.fake_message(Invoked(client_id=333, output=22))
        self.network.tick(INVOKE_RETRANSMIT)
        self.assertMessage(['F999'], Invoke(caller='F999', client_id=CLIENT_ID, input_value=10))
        self.assertFalse(self.callback.called)
        self.node.fake_message(Invoked(client_id=CLIENT_ID, output=20))
        self.callback.assert_called_with(20)
        self.assertUnregistered()
