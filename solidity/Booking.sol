pragma solidity ^0.8.0;

// Author:	Louis Holbrook <dev@holbrook.no> 0826EDA1702D1E87C6E2875121D2E7BB88C2A746
// SPDX-License-Identifier: AGPL-3.0-or-later
// File-Version: 1
// Description: Time slot booking 


contract ERC20Book {
	// Implements ERC173
	address public owner;
	address public token;
	bytes slots;
	bytes sharedSlots;
	uint256 public capacity;
	uint256 public totalSupply;
	uint256 public originalTokenSupply;
	uint256 public shareCount;
	mapping ( address => uint256 ) shares;
	mapping ( address => bool ) writers;

	// Implements Seal
	event SealStateChange(bool indexed _final, uint256 _sealState);

	uint256 public sealState;
	uint8 constant WRITER_STATE = 1;
	uint256 constant public maxSealState = 1;

	constructor (address _token, uint256 _resolution) {
		require(_resolution > 0 && _resolution < (1 << 128), "ERR_NONSENSE");
		uint256[2] memory r;

		r = getPos(_resolution);
		slots = new bytes(r[0] + 1);
		sharedSlots = new bytes(r[0] + 1);
		capacity = _resolution;
		totalSupply = capacity;
		token = _token;
		originalTokenSupply = tokenSupply();
		owner = msg.sender;
	}

	function seal(uint256 _state) public returns(uint256) {
		require(_state < maxSealState + 1, 'ERR_INVALID_STATE');
		require(_state & sealState == 0, 'ERR_ALREADY_LOCKED');
		sealState |= _state;
		emit SealStateChange(sealState == maxSealState, sealState);
		return uint256(sealState);
	}

	function isSealed(uint256 _state) public view returns(bool) {
		require(_state < maxSealState);
		if (_state == 0) {
			return sealState == maxSealState;
		}
		return _state & sealState == _state;
	}

	// Implements Writer
	function addWriter(address _writer) public returns (bool) {
		require(!isSealed(WRITER_STATE), "ERR_SEALED");
		require(msg.sender == owner, "ERR_AXX");
		writers[_writer] = true;
		return true;
	}

	// Implements Writer
	function removeWriter(address _writer) public returns (bool) {
		require(!isSealed(WRITER_STATE), "ERR_SEALED");
		require(msg.sender == owner || msg.sender == _writer, "ERR_AXX");
		writers[_writer] = false;
		return true;
	}

	// Implements Writer
	function isWriter(address _writer) public view returns (bool) {
		return writers[_writer] || _writer == owner;
	}

	function depositFor(address _spender) public returns (int256) {
		uint256 l_limit;
		uint256 l_unit;
		int256 l_value;
		bool r;
		bytes memory v;
		address l_sender;
		address l_receiver;

		l_unit = unitValue();	
		//return shareCount * l_unit;
		l_limit = shareCount * l_unit;
		if (l_limit == shares[_spender]) {
			return 0;
		}

		l_value = int256(l_limit) - int256(shares[_spender]);
		if (l_limit > shares[_spender]) {
			l_sender = _spender;
			l_receiver = address(this);
		} else {
			l_sender = address(this);
			l_receiver = _spender;
			l_value *= -1;
		}

		(r, v) = token.call(abi.encodeWithSignature('transferFrom(address,address,uint256)', l_sender, l_receiver, uint256(l_value)));
		require(r, "ERR_TOKEN");
		r = abi.decode(v, (bool));
		require(r, "ERR_TRANSFER");

		shares[_spender] = l_limit;
		return l_value;
	}

	function deposit() public returns(int256) {
		return depositFor(msg.sender);
	}

	function unitValue() internal returns(uint256) {
		uint256 l_supply;
		uint256 l_unit;

		l_supply = tokenSupply();
		require(l_supply == originalTokenSupply, "ERR_SUPPLY_CHANGED");
		require(l_supply >= totalSupply, "ERR_SUPPLY_UNDERFLOW");
		l_unit = l_supply / totalSupply;
		return l_unit;
	}

	function tokenSupply() internal returns (uint256) {
		bool r;
		bytes memory v;
		uint256 l_supply;

		(r, v) = token.call(abi.encodeWithSignature('totalSupply()'));
		require(r, "ERR_TOKEN");
		l_supply = abi.decode(v, (uint256));

		return l_supply;
	}

	function consume(uint256 _offset, uint256 _count) public {
		bool r;
		bytes memory v;
		uint256 l_value;

		l_value = unitValue() * _count;
		(r, v) = token.call(abi.encodeWithSignature('transferFrom(address,address,uint256)', msg.sender, this, l_value));
		require(r, "ERR_TOKEN");
		r = abi.decode(v, (bool));
		require(r, "ERR_TRANSFER");

		reserve(_offset, _count, false);
	}

	function share(uint256 _offset, uint256 _count) public {
		require(isWriter(msg.sender), "ERR_AXX");
		reserve(_offset, _count, true);
	}

	// improve by comparing word by word
	function reserve(uint256 _offset, uint256 _count, bool _share) internal {
		require(_count > 0, "ERR_ZEROCOUNT");
		uint256[2] memory c;
		uint256 cy;
		uint8 ci;

		c = getPos(_offset);
		cy = c[0];
		ci = uint8(1 << (uint8(c[1])));
		for (uint256 i = 0; i < _count; i++) {
			require(capacity > 0, "ERR_CAPACITY");
			require(slotAvailable(cy, ci), "ERR_COLLISION");
			if (_share) {
				sharedSlots[cy] = bytes1(uint8(sharedSlots[cy]) | ci);
				shareCount++;
			} else {
				slots[cy] = bytes1(uint8(slots[cy]) | ci);
			}
			if (ci == 128) {
				cy++;
				ci = 1;
			} else {
				ci <<= 1;
			}
			capacity--;
		}
	}

	function slotAvailable(uint256 _byte, uint8 _bitVal) internal view returns (bool) {
		return (uint8(slots[_byte]) | uint8(sharedSlots[_byte])) & _bitVal == 0;
	}

	function getPos(uint256 bit) internal pure returns (uint256[2] memory) {
		int256 c;
		uint256[2] memory r;

		c = int256(bit) / 8;

		r[0] = uint256(c);
		r[1] = bit % 8;
		return r;
	}

	function raw(uint256 _count, uint256 _offset) public view returns (bytes memory) {
		bytes memory r;
		uint256[2] memory c;
		uint256 l_offset;
		uint256 l_count;

		if (_count == 0) {
			_count = capacity / 8;
		}
		require(_offset % 8 == 0, "ERR_BOUNDARY");

		c = getPos(_offset);
		l_offset = uint256(c[0]);

		l_count = _count / 8;
		if (uint8(c[1]) > 1) {
			l_count += 1;
		}
		r = new bytes(l_count);
		for (uint256 i = 0; i < l_count; i++) {
			r[i] = slots[i + l_offset] | sharedSlots[i + l_offset];
		}
		return r;
	}
}
