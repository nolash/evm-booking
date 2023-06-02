# standard imports
import datetime
import logging

# external imports
from chainlib.eth.tx import TxFormat

# local imports
from evm_booking import Booking

logg = logging.getLogger(__name__)

PERIOD_HALFHOUR = 60*30
PERIOD_HOUR = PERIOD_HALFHOUR * 2
PERIOD_DAY = PERIOD_HOUR * 24
PERIOD_YEAR = PERIOD_DAY * 365
PERIOD_LEAPYEAR = PERIOD_YEAR + PERIOD_DAY


class TimeBooking(Booking):

    def __init__(self, chain_spec, period_seconds, resolution_seconds, start_seconds=None, signer=None, gas_oracle=None, nonce_oracle=None):
        super(TimeBooking, self).__init__(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)
        if period_seconds % resolution_seconds > 0:
            raise ValueError("period must be evenly divided in resolution")
        self.start = None
        self.end = None
        duration = period_seconds * resolution_seconds
        if start_seconds != None:
            self.start = datetime.datetime.fromtimestamp(start_seconds)
            self.end = self.start + datetime.timedelta(seconds=duration + 1)
        self.unit = resolution_seconds
        self.capacity_units = int(period_seconds / resolution_seconds)


    def constructor(self, sender_address, token_address, tx_format=TxFormat.JSONRPC, version=None):
        return super(TimeBooking, self).constructor(sender_address, token_address, self.capacity_units, self.end, tx_format=tx_format, version=version)


    def share_date(self, contract_address, sender_address, start_date, count, ref_date=None, tx_format=TxFormat.JSONRPC, id_generator=None):
        offset = self.offset_from_date(start_date, count, ref_date=ref_date)
        return super(TimeBooking, self).share(contract_address, sender_address, offset, count)


    def consume_date(self, contract_address, sender_address, start_date, count, ref_date=None, tx_format=TxFormat.JSONRPC, id_generator=None):
        offset = self.offset_from_date(start_date, count, ref_date=ref_date)
        return super(TimeBooking, self).consume(contract_address, sender_address, offset, count)


    def offset_from_date(self, start_date, count, ref_date=None):
        if ref_date == None:
            ref_date = self.start
        if ref_date == None:
            raise AttributeError('no reference start date exists')

        duration = datetime.timedelta(seconds=count*self.unit)
        end_seconds = self.capacity_units * self.unit
        end_date = ref_date + datetime.timedelta(seconds=end_seconds)
        target_date = start_date + duration
        logg.debug("ref {} {}".format(end_seconds, ref_date))
        if target_date > end_date:
            raise ValueError('duration results in {} which is beyond end date {}'.format(target_date, end_date))

        delta = start_date - ref_date
        if delta.seconds % self.unit > 0:
            raise ValueError('start date must be evenly divide into unit of {} seconds'.format(self.unit))
        offset = (delta.days * 24*60*60) / self.unit
        offset += int(delta.seconds / self.unit)
        return offset
