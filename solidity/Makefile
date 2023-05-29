SOLC = /usr/bin/solc

all:
	$(SOLC) --bin Booking.sol --evm-version byzantium | awk 'NR>3' > Booking.bin
	$(SOLC) --abi Booking.sol --evm-version byzantium | awk 'NR>3' > Booking.json
	$(SOLC) --metadata Booking.sol --evm-version byzantium | awk 'NR>3' > Booking.metadata.json
	truncate -s -1 Booking.bin

install: all
	cp -v *.json ../python/evm_booking/data/
	cp -v *.bin ../python/evm_booking/data/

