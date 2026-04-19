/* Bounded string / integer formatting helpers used by the asm modules.
 *
 * All helpers take a (dst, end) pair: they write to *dst and never write past
 * *end, returning the updated dst cursor in x0. Callers reserve end = buf +
 * buflen - 1 and write a trailing NUL themselves.
 *
 * No variadic calls (cause of earlier ARM64 ABI pitfalls with snprintf).
 */
    .text
    .align 2

    /*
     * char *pfs_str_append(char *dst, char *end, const char *src);
     * Copies bytes from src into dst until NUL or dst == end.
     */
    .globl _pfs_str_append
_pfs_str_append:
.Lsa_loop:
    cmp x0, x1
    b.hs .Lsa_done
    ldrb w3, [x2], #1
    cbz w3, .Lsa_done
    strb w3, [x0], #1
    b .Lsa_loop
.Lsa_done:
    ret

    /*
     * char *pfs_u32_append(char *dst, char *end, uint32_t val);
     * Writes decimal digits into [dst, end). Always emits at least "0".
     */
    .globl _pfs_u32_append
_pfs_u32_append:
    sub sp, sp, #16
    mov x3, sp                  /* scratch start */
    mov x4, x3                  /* scratch cursor */
    mov w5, #10
.Lua_gen:
    udiv w6, w2, w5
    msub w7, w6, w5, w2
    add w7, w7, #'0'
    strb w7, [x4], #1
    mov w2, w6
    cbnz w2, .Lua_gen
.Lua_rev:
    sub x4, x4, #1
    cmp x0, x1
    b.hs .Lua_out
    ldrb w6, [x4]
    strb w6, [x0], #1
    cmp x4, x3
    b.hi .Lua_rev
.Lua_out:
    add sp, sp, #16
    ret

    /*
     * char *pfs_u64_append(char *dst, char *end, uint64_t val);
     */
    .globl _pfs_u64_append
_pfs_u64_append:
    sub sp, sp, #32
    mov x3, sp
    mov x4, x3
    mov x5, #10
.Lla_gen:
    udiv x6, x2, x5
    msub x7, x6, x5, x2
    add x7, x7, #'0'
    strb w7, [x4], #1
    mov x2, x6
    cbnz x2, .Lla_gen
.Lla_rev:
    sub x4, x4, #1
    cmp x0, x1
    b.hs .Lla_out
    ldrb w6, [x4]
    strb w6, [x0], #1
    cmp x4, x3
    b.hi .Lla_rev
.Lla_out:
    add sp, sp, #32
    ret
