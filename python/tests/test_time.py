# standard imports
import unittest
import logging
import datetime

# external imports
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import TxFactory
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from eth_erc20 import ERC20
from giftable_erc20_token.unittest import TestGiftableToken

# local imports
from evm_booking.unittest import TestBooking
from evm_booking.time import *

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestBookingTime(TestGiftableToken):

    def setUp(self):
        super(TestBookingTime, self).setUp()
        self.token_address = self.address

        d = datetime.datetime(year=1984, month=1, day=1)
        d = int(d.timestamp())
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        c = TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR, start_seconds=d, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0], self.token_address)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
        self.address = to_checksum_address(r['contract_address'])
        self.booking_address = self.address
        self.caller = TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR, start_seconds=d)


    def test_uneven(self):
        d = datetime.datetime(year=1984, month=1, day=1)
        d = int(d.timestamp())
        with self.assertRaises(ValueError):
            TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR - 1, start_seconds=d)


    def test_check_capacity(self):
        logg.debug('foo {}'.format(self.caller.capacity))
        o = self.caller.capacity(self.booking_address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        capacity = int(r, 16)
        self.assertEqual(capacity, int(PERIOD_LEAPYEAR / PERIOD_HALFHOUR))


    def test_by_date(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        d = datetime.datetime(year=1984, month=1, day=1)
        c = TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR, start_seconds=d.timestamp(), signer=self.signer, nonce_oracle=nonce_oracle)
        start_date = datetime.datetime(year=1984, month=3, day=8, hour=12, minute=30)
        count = int(PERIOD_DAY / PERIOD_HALFHOUR)
        (tx_hash, o) = c.share_date(self.booking_address, self.accounts[0], start_date, count)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.raw(self.booking_address, count=80, offset=3216, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        raw = c.parse_raw(r)
        self.assertEqual("000000feffffffffff01", raw)


    def test_consume_by_date(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.rpc)
        d = datetime.datetime(year=1984, month=1, day=1)
        start_date = datetime.datetime(year=1984, month=3, day=8, hour=12, minute=30)
        count = int(PERIOD_DAY / PERIOD_HALFHOUR)
        c = TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR, start_seconds=d.timestamp(), signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.consume_date(self.booking_address, self.accounts[0], start_date, count)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.approve(self.token_address, self.accounts[0], self.address, self.initial_supply)
        self.rpc.do(o)

        c = TimeBooking(self.chain_spec, PERIOD_LEAPYEAR, PERIOD_HALFHOUR, start_seconds=d.timestamp(), signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.consume_date(self.booking_address, self.accounts[0], start_date, count)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.raw(self.booking_address, count=80, offset=3216, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        raw = c.parse_raw(r)
        self.assertEqual("000000feffffffffff01", raw)


if __name__ == '__main__':
    unittest.main()
