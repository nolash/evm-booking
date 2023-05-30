pragma solidity ^0.8.0;

// Author:	Louis Holbrook <dev@holbrook.no> 0826EDA1702D1E87C6E2875121D2E7BB88C2A746
// SPDX-License-Identifier: AGPL-3.0-or-later
// File-Version: 1
// Description: Time slot booking 


contract ERC20Book {
	bytes slots;
	uint256 cap;

	constructor (uint256 _resolution) {
		require(_resolution > 0 && _resolution < (1 << 128), "ERR_NONSENSE");
		uint256[2] memory r;

		r = getPos(_resolution);
		slots = new bytes(r[0] + 1);
		cap = _resolution;
	}

	// improve by comparing word by word
	function reserve(uint256 _offset, uint256 _count) public {
		require(_count > 0, "ERR_ZEROCOUNT");
		uint256[2] memory c;
		uint256 cy;
		uint8 ci;

		c = getPos(_offset);
		cy = c[0];
		ci = uint8(1 << (uint8(c[1])));
		for (uint256 i = 0; i < _count; i++) {
			require(cap > 0, "ERR_CAPACITY");
			if (uint8(slots[cy]) & ci > 0) {
				revert("ERR_COLLISION");
			}
			slots[cy] = bytes1(uint8(slots[cy]) | ci);
			if (ci == 128) {
				cy++;
				ci = 1;
			} else {
				ci <<= 1;
			}
			cap--;
		}
	}

	function getPos(uint256 bit) internal pure returns (uint256[2] memory) {
		int256 c;
		uint256[2] memory r;

		c = (int256(bit) - 1) / 8 + 1 ;

		r[0] = uint256(c);
		r[1] = bit % 8;
		return r;
	}
}
