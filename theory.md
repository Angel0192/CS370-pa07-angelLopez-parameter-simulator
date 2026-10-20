# PA 7: The Parameter Simulator — Part A

**CS 379: Programming Languages, Fall 2026**
**Angel Lopez**

Notation: `name → [v]` means the name points to a Cell holding `v`. If two names point to the same Cell, they're aliases.

## Verification question

| Mode | Who owns the writable Cell | When the caller sees a write | Test that catches a bad implementation |
|---|---|---|---|
| Value | The callee (new private Cell) | Never | "value mode allocates a separate Cell" |
| Reference | The caller (shared Cell) | Right away | "reference write is visible before return" |
| Value-result | The callee, then copied to the caller | Only at return | "value-result write is hidden before return", P(a,a) = 11 |

Python sharing a list is object aliasing, not USILang pass-by-reference. Pass-by-reference shares the Cell itself.

---

## 1. Three Modes, One Function

`swap(a, b) { let t = a; a = b; b = t; }` called as `swap(x, y)` with `x = 1`, `y = 2`.

### Pass-by-value

| Step | Caller | Callee AR |
|---|---|---|
| Entry | `x → [1]`, `y → [2]` | `a → [1]`, `b → [2]` (new Cells) |
| `let t = a;` | `x → [1]`, `y → [2]` | `a → [1]`, `b → [2]`, `t → [1]` |
| `a = b;` | `x → [1]`, `y → [2]` | `a → [2]`, `b → [2]`, `t → [1]` |
| `b = t;` | `x → [1]`, `y → [2]` | `a → [2]`, `b → [1]`, `t → [1]` |
| Return | nothing copied back | AR thrown away |

**x = 1, y = 2.** The swap only happened in the callee's own Cells.

### Pass-by-reference

| Step | Caller | Callee AR |
|---|---|---|
| Entry | `x → C1[1]`, `y → C2[2]` | `a → C1`, `b → C2` (shared) |
| `let t = a;` | `C1[1]`, `C2[2]` | `t → [1]` (new local) |
| `a = b;` | `C1[2]`, `C2[2]` | writes into C1 |
| `b = t;` | `C1[2]`, `C2[1]` | writes into C2 |
| Return | nothing to copy | — |

**x = 2, y = 1.** Every write changed the caller right away.

### Pass-by-value-result

| Step | Caller | Callee AR |
|---|---|---|
| Entry | `x → C1[1]`, `y → C2[2]` | `a → [1]`, `b → [2]` (copies); saved: `a → C1`, `b → C2` |
| `let t = a;` | `C1[1]`, `C2[2]` | `a → [1]`, `b → [2]`, `t → [1]` |
| `a = b;` | `C1[1]`, `C2[2]` | `a → [2]`, `b → [2]`, `t → [1]` |
| `b = t;` | `C1[1]`, `C2[2]` | `a → [2]`, `b → [1]`, `t → [1]` |
| Copy `a → C1` | `C1[2]`, `C2[2]` | — |
| Copy `b → C2` | `C1[2]`, `C2[1]` | — |

**x = 2, y = 1.** Same answer as reference, but the caller doesn't see it until return.

---

## 2. Asymmetric Aliasing

`P(x, y) { x = x + 1; y = y + 1; }` called as `P(a, a)` with `a = 10`.

### Pass-by-reference

| Step | Shared Cell (a, x, y) |
|---|---|
| Entry | 10 |
| `x = x + 1;` | 11 |
| `y = y + 1;` (reads 11) | 12 |
| Return | nothing to copy |

**a = 12.** Both names share one Cell, so the second increment builds on the first.

### Pass-by-value-result

| Step | Caller `a` | `x` | `y` |
|---|---|---|---|
| Entry | 10 | 10 | 10 |
| `x = x + 1;` | 10 | 11 | 10 |
| `y = y + 1;` | 10 | 11 | 11 |
| Copy `x → a` | 11 | — | — |
| Copy `y → a` | 11 | — | — |

**a = 11.** Each parameter bumped its own copy from 10 to 11, so neither saw the other's change. Copy-back writes 11 into `a` twice, with `y` last.

The difference comes from one shared Cell vs. two private ones. A symmetric `swap(a, a)` can't show this because swapping a value with itself does nothing in either mode.

---

## 3. Closures and Capture

```
let makers = [];
for (i = 0; i < 3; i = i + 1) {
    makers.push(func() { return i; });
}
```

**All three closures return 3.** There's only one `i` Cell, and every closure captures the same environment that holds it.

When a closure is called, its new environment's parent is that captured environment, which works like the static link from PA 6. Looking up `i` follows the static link to the shared Cell, and after the loop ends that Cell holds 3.

**Fix:** have `for` make a new environment with a fresh `i` Cell each iteration, copied from the last iteration's value. Each closure then links to its own iteration's Cell and returns 0, 1, or 2, like `let` in a JavaScript `for` loop.