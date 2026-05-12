// Package coinbank implements the business logic of the coin-exchange
// machine specified by variant 2 of the lab handout: it identifies which
// denomination is acceptable, knows how to add an incoming coin to the
// change pool, and computes whether a given coin can be exchanged into
// coins of the requested denomination.
//
// The machine accepts coins of 1, 2, 5, 10, 25, 50 kopiykas and 1 hryvnia
// (100 kopiykas).  The change pool stores only the 6 kopiyka denominations.
package coinbank

import "lab3/internal/shm"

// Outcome describes the result of a single change-making attempt.
type Outcome struct {
	OK         bool
	RefuseCode int32   // 0 on success, otherwise one of shm.Refuse*
	Coin       int32   // input coin (kopiykas)
	Denom      int32   // requested denomination (kopiykas)
	Count      int32   // number of coins dispensed on success
}

// IndexOfBankDenom returns the position of denom in shm.BankDenominations
// or -1 when the denomination is not one of the change-pool denominations.
func IndexOfBankDenom(denom int32) int {
	for i, d := range shm.BankDenominations {
		if d == denom {
			return i
		}
	}
	return -1
}

// IsAcceptedCoin reports whether coin is one of the seven accepted
// denominations.
func IsAcceptedCoin(coin int32) bool {
	for _, d := range shm.Denominations {
		if d == coin {
			return true
		}
	}
	return false
}

// AddIncoming adds an accepted coin to the change pool if it belongs to
// the 6-denomination kopiyka set.  The 1 hryvnia coin is accepted but is
// not used as change (it sits in the cash drawer of the device, modelled
// implicitly).  Returns the index that was incremented or -1 if nothing
// was added.
func AddIncoming(bank *[6]int32, coin int32) int {
	idx := IndexOfBankDenom(coin)
	if idx >= 0 {
		bank[idx]++
	}
	return idx
}

// MakeChange tries to break coin into coins of the given denomination.
// On success it decrements the bank by the number of coins dispensed and
// returns Outcome{OK: true, Count: coin/denom}.
//
// Four refuse reasons are produced, matching the codes declared in package
// shm:
//   1. RefuseInvalidDenom    — denom is not one of 1,2,5,10,25,50.
//   2. RefuseDenomGEQCoin    — denom >= coin (cannot break into the same
//                              or bigger denomination).
//   3. RefuseIndivisible     — coin is not a multiple of denom.
//   4. RefuseInsufficientBox — the change pool does not contain enough
//                              coins of the requested denomination.
func MakeChange(bank *[6]int32, coin, denom int32) Outcome {
	out := Outcome{Coin: coin, Denom: denom}

	idx := IndexOfBankDenom(denom)
	if idx < 0 {
		out.RefuseCode = shm.RefuseInvalidDenom
		return out
	}
	if denom >= coin {
		out.RefuseCode = shm.RefuseDenomGEQCoin
		return out
	}
	if coin%denom != 0 {
		out.RefuseCode = shm.RefuseIndivisible
		return out
	}
	count := coin / denom
	if bank[idx] < count {
		out.RefuseCode = shm.RefuseInsufficientBox
		return out
	}

	bank[idx] -= count
	out.OK = true
	out.Count = count
	return out
}

// RefuseText maps a refuse code into a human-readable reason for the GUI.
func RefuseText(code int32) string {
	switch code {
	case shm.RefuseInvalidDenom:
		return "невірний номінал розміну"
	case shm.RefuseDenomGEQCoin:
		return "номінал розміну не менший за монету"
	case shm.RefuseIndivisible:
		return "монета не ділиться на номінал без остачі"
	case shm.RefuseInsufficientBox:
		return "недостатньо монет потрібного номіналу в банку"
	default:
		return ""
	}
}
