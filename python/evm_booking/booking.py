# standard imports
import logging
import os
import enum

# external imports
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import (
    ABIContractEncoder,
    ABIContractDecoder,
    ABIContractType,
    abi_decode_single,
)
from chainlib.eth.jsonrpc import to_blockheight_param
from chainlib.eth.error import RequestMismatchException
from chainlib.eth.tx import (
    TxFactory,
    TxFormat,
)
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.block import BlockSpec
from hexathon import (
    add_0x,
    strip_0x,
)
from chainlib.eth.cli.encode import CLIEncoder

# local imports
from evm_booking.data import data_dir

logg = logging.getLogger()



class Booking(TxFactory):

    __abi = None
    __bytecode = None

    def constructor(self, sender_address, cap, tx_format=TxFormat.JSONRPC, version=None):
        code = self.cargs(cap, version=version)
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.finalize(tx, tx_format)


    @staticmethod
    def cargs(cap, version=None):
        code = Booking.bytecode(version=version)
        enc = ABIContractEncoder()
        enc.uint256(cap)
        args = enc.get()
        code += args
        logg.debug('constructor code: ' + args)
        return code


    @staticmethod
    def gas(code=None):
        return 4000000



    @staticmethod
    def abi():
        if Booking.__abi == None:
            f = open(os.path.join(data_dir, 'Booking.json'), 'r')
            Booking.__abi = json.load(f)
            f.close()
        return Booking.__abi


    @staticmethod
    def bytecode(version=None):
        if Booking.__bytecode == None:
            f = open(os.path.join(data_dir, 'Booking.bin'))
            Booking.__bytecode = f.read()
            f.close()
        return Booking.__bytecode

    
    def reserve(self, contract_address, sender_address, offset, count, tx_format=TxFormat.JSONRPC, id_generator=None):
        enc = ABIContractEncoder()
        enc.method('reserve')
        enc.typ(ABIContractType.UINT256)
        enc.typ(ABIContractType.UINT256)
        enc.uint256(offset)
        enc.uint256(count)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format, id_generator=id_generator)
        return tx
