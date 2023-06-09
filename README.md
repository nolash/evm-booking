# evm-booking

# Overview

This EVM smart contract allows exchanging ERC20 tokens for generic
serial units.

The primary use-case is time-slot booking.

Unit ranges may also be reserved for collective use. In this case, token
holders must pledge a proportional amount of their holdings towards the
shared units.

## Example

Alice and Bob hold ‘`TIME`’ vouchers.

Each ‘`TIME`’ voucher unit represents one hour of time with a really
comfortable hammock on the beach.

Unfortunately, the beach is not accessible all the time, because local
technocrat authorities have decided to close the beach for the public
every day from 6pm to 6am on every weekday, to protect people from their
own pleasure-seeking.

Their trusted friend Trent publishes the ‘`evm-booking`’ contract, to
manage hammock time for the coming month.

The month has 30 days. The period starts on a wednesday (6am) and ends
on a friday (6am).

The period has 22 weekdays and 8 weekend days. This translates to
$(22 * 12) + (8 * 24) = 264 + 192 = 456$ hours of available hammock
time.

456.00 ‘`TIME`’ vouchers are minted (two decimal places).

Since Alice paid more for the hammock, she gets 60% of the time. Thus
Alice has 273.6 and Bob has 182.4.

### Collective use

Alice and Bob decide that they will rent the hammock out on weekends
through Trent, and share in the proceeds. The rest of the time, they can
reserve hammock time for themselves, or sell hammock time on to others.

Trent reserves 192 hours in the contract for collective use, and Alice
and Bob has to pledge $192 * 60% = 115.2$ and $192 * 0.4 = 76.8$
vouchers respectively to cover that use.

Trent will be selling hammock time for Generic Fiat Currency (GFC), and
will get 30% off the top for the bother.

### Individual use

Alice spends a total of 100 hours on the hammock. Her remaining 15.2
hours are unused, during which time the hammock is very lonely.

Bob sells 10 hours of hammock use to each Carol and Dave, and uses every
bit of remaining time himself.

Dave is too busy for hammocking. He spends 2 hours and sells 8 remaining
hours to Frank.

### Fruits of use

Trent was able to cash in a tidy 200 GFC for the time. He takes 60 GFC
for himself. According to their shares, Alice gets 84 GFC and Bob gets
56 GFC.

# Smart contract

When the smart contract is published, it is bound to:

- The ERC20 token that will be used to spend serial units.

- The amount of serial units.

- Timestamp until when serial units can be reserved and spent.

The supply of the ERC20 token will be read and stored, and used to
calculate shares for collective use.

**The supply of the ERC20 token must not change after binding it to the
contract**.

## Interface

The contract interface consists of three main methods.

`consume`  
Will spend serial units in the contract, and invoke `ERC20.transferFrom`
to cover those units.

`share`  
Reserve serial units for collective use. Requires all token holders to
collectively deposit a corresponding share of the total supply.

`deposit(For)`  
Manually synchronise deposits to cover the time currently reserved for
collective use.

## Expiration

After expiration, the shares of the collective use are considered
finalized, and can be read out from the contract.

## Raw output

The `raw` method returns the bit field representing the state of
individual serial slots.

### Example

Let the total of time slots be 50.

Slots (inclusive, zero-indexed) 13-30 have been *spent* (`consume`) and
249-255 have been *reserved* (`share`).

Calling `raw(11, 257)` will yield a virtual bit field (lowest index
left) as follows:

    00111111 11111111 11110000 00000000 (bytes 0-4)
    [...]
    00000000 00000011 11111000 00000000 (bytes 28-31)
    0 (bit 257)

The ABI encoded return value will be, grouped by word:

    0000000000000000000000000000000000000000000000000000000000000020
    0000000000000000000000000000000000000000000000000000000000000021
    008f300000000000000000000000000000000000000000ffffffffffffffff3f
    0000000000000000000000000000000000000000000000000000000000000000

The bit field is read word for word, then byte-for-byte from right to
left.

Note how it merges both the *spent* and *reserved* slots.
