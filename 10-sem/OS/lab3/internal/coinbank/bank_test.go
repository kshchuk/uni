package coinbank

import (
	"testing"

	"lab3/internal/shm"
)

func TestMakeChangeSuccess(t *testing.T) {
	bank := [6]int32{50, 25, 20, 15, 10, 5}
	out := MakeChange(&bank, 10, 2)
	if !out.OK {
		t.Fatalf("expected success, got refuse=%d", out.RefuseCode)
	}
	if out.Count != 5 {
		t.Fatalf("expected 5 coins, got %d", out.Count)
	}
	if bank[1] != 20 {
		t.Fatalf("bank[2k] expected 20, got %d", bank[1])
	}
}

func TestMakeChangeRefusalInvalidDenom(t *testing.T) {
	bank := [6]int32{}
	out := MakeChange(&bank, 10, 3)
	if out.OK || out.RefuseCode != shm.RefuseInvalidDenom {
		t.Fatalf("expected RefuseInvalidDenom, got OK=%v code=%d", out.OK, out.RefuseCode)
	}
}

func TestMakeChangeRefusalDenomGEQCoin(t *testing.T) {
	bank := [6]int32{0, 0, 100, 0, 0, 0}
	out := MakeChange(&bank, 5, 5)
	if out.OK || out.RefuseCode != shm.RefuseDenomGEQCoin {
		t.Fatalf("expected RefuseDenomGEQCoin, got OK=%v code=%d", out.OK, out.RefuseCode)
	}
	out = MakeChange(&bank, 5, 10)
	if out.OK || out.RefuseCode != shm.RefuseDenomGEQCoin {
		t.Fatalf("expected RefuseDenomGEQCoin, got OK=%v code=%d", out.OK, out.RefuseCode)
	}
}

func TestMakeChangeRefusalIndivisible(t *testing.T) {
	bank := [6]int32{0, 100, 0, 0, 0, 0}
	out := MakeChange(&bank, 5, 2) // 5 / 2 -> остача 1
	if out.OK || out.RefuseCode != shm.RefuseIndivisible {
		t.Fatalf("expected RefuseIndivisible, got OK=%v code=%d", out.OK, out.RefuseCode)
	}
}

func TestMakeChangeRefusalInsufficientBox(t *testing.T) {
	bank := [6]int32{2, 0, 0, 0, 0, 0} // тільки 2 коп. по 1
	out := MakeChange(&bank, 10, 1)    // потрібно 10 шт.
	if out.OK || out.RefuseCode != shm.RefuseInsufficientBox {
		t.Fatalf("expected RefuseInsufficientBox, got OK=%v code=%d", out.OK, out.RefuseCode)
	}
}

func TestAddIncomingHryvniaIgnored(t *testing.T) {
	bank := [6]int32{}
	if idx := AddIncoming(&bank, 100); idx != -1 {
		t.Fatalf("1 hryvnia must not be added to change pool, idx=%d", idx)
	}
	if AddIncoming(&bank, 5) != 2 {
		t.Fatalf("expected index 2 for 5 kop")
	}
	if bank[2] != 1 {
		t.Fatalf("expected bank[2]=1, got %d", bank[2])
	}
}

func TestIsAcceptedCoin(t *testing.T) {
	for _, c := range []int32{1, 2, 5, 10, 25, 50, 100} {
		if !IsAcceptedCoin(c) {
			t.Fatalf("expected %d accepted", c)
		}
	}
	for _, c := range []int32{0, 3, 4, 75, 200} {
		if IsAcceptedCoin(c) {
			t.Fatalf("expected %d rejected", c)
		}
	}
}

func TestMakeChange1HryvniaInto25Kop(t *testing.T) {
	bank := [6]int32{0, 0, 0, 0, 4, 0}
	out := MakeChange(&bank, 100, 25)
	if !out.OK || out.Count != 4 {
		t.Fatalf("expected 4 coins, OK=%v code=%d count=%d", out.OK, out.RefuseCode, out.Count)
	}
	if bank[4] != 0 {
		t.Fatalf("expected bank[25k]=0, got %d", bank[4])
	}
}
