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

    def test_base(self):
        pass


if __name__ == '__main__':
    unittest.main()
