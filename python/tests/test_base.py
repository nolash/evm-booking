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
        self.assertEqual(r['status'], 0)

        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.approve(self.token_address, self.accounts[0], self.address, self.initial_supply)
        self.rpc.do(o)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = ERC20(self.chain_spec)
        o = c.balance_of(self.token_address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance_of(r)
        expected_balance = self.initial_supply - (self.resolution_unit * 13)
        self.assertEqual(balance, expected_balance)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
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


    def test_deposit_excess(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.approve(self.token_address, self.accounts[0], self.address, self.initial_supply)
        self.rpc.do(o)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.share(self.address, self.accounts[0], 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.deposit(self.address, self.accounts[0])
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = ERC20(self.chain_spec)
        o = c.balance_of(self.token_address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance_of(r)
        expected_balance = self.initial_supply - (self.resolution_unit * 13)
        self.assertEqual(balance, expected_balance)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.deposit(self.address, self.accounts[0])
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = ERC20(self.chain_spec)
        o = c.balance_of(self.token_address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance_of(r)
        self.assertEqual(balance, expected_balance)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.share(self.address, self.accounts[0], 133, 7)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.deposit(self.address, self.accounts[0])
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = ERC20(self.chain_spec)
        o = c.balance_of(self.token_address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance_of(r)
        expected_balance = self.initial_supply - (self.resolution_unit * (13 + 7))
        self.assertEqual(balance, expected_balance)


    def test_raw(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.approve(self.token_address, self.accounts[0], self.address, self.initial_supply)
        self.rpc.do(o)

        c = Booking(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.share(self.address, self.accounts[0], 42, 13)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.consume(self.address, self.accounts[0], 133, 7)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.raw(self.address, sender_address=self.accounts[0], count=160)
        r = self.rpc.do(o)
        field = c.parse_raw(r)
        self.assertEqual("0000000000fc7f000000000000000000e00f0000", field)


if __name__ == '__main__':
    unittest.main()
