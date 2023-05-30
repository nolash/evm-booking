# standard imports
import unittest
import logging
import os
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from eth_erc20 import ERC20
from giftable_erc20_token import GiftableToken

# local imports
from evm_booking.unittest import TestBooking
from evm_booking import Booking


logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestBookingBase(TestBooking):

    def setUp(self):
        super(TestBookingBase, self).setUp()
        self.publish()


    def test_base(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 42, 1)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)
 
        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 42+13-1, 1)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 41, 1)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 42+13, 1)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)


    def test_axx(self):
        nonce_oracle = RPCNonceOracle(self.alice, conn=self.rpc)
        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.share(self.address, self.alice, 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.share(self.address, self.accounts[0], 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)


if __name__ == '__main__':
    unittest.main()
