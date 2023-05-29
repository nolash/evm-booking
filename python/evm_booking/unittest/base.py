# standard imports
import logging
import time

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from giftable_erc20_token.unittest import TestGiftableToken
from evm_booking import Booking
from chainlib.eth.block import block_latest

# local imports
from evm_booking import Booking


logg = logging.getLogger(__name__)

class TestBooking(TestGiftableToken):

    expire = 0

    def setUp(self):
        super(TestBooking, self).setUp()

        self.alice = self.accounts[1]
        self.bob = self.accounts[2]

        self.token_address = self.address


    def publish(self, mint=False, decimals=0):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0], 366 * 24)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
        self.vend_address = to_checksum_address(r['contract_address'])
        logg.debug('published booker on address {} with hash {}'.format(self.vend_address, tx_hash))
