/*
 * PNG IHDR parsing for the detail panel.
 */
    .text
    .align 2

    .extern _open
    .extern _read
    .extern _close
    .extern _snprintf

    .equ O_RDONLY, 0

    .bss
    .align 4
png_readbuf:
    .space 8192

    .section __TEXT,__cstring,cstring_literals
png_fmt:
    .asciz "PNG IHDR preview\nDimensions: %u x %u px\nBit depth: %u\nColor type: %u\nInterlace: %u"

    .text

    .globl _png_format_ihdr_info
_png_format_ihdr_info:
    stp x29, x30, [sp, #-64]!
    mov x29, sp
    stp x19, x22, [sp, #16]

    mov x19, x0
    mov x20, x1
    mov x21, x2

    mov x0, x19
    mov w1, #O_RDONLY
    bl _open
    cmp x0, #0
    b.lt .Lpf_fail
    mov x22, x0

    mov x0, x22
    adrp x1, png_readbuf@PAGE
    add x1, x1, png_readbuf@PAGEOFF
    mov x2, #8192
    bl _read
    cmp x0, #33
    b.lo .Lpf_bad_read

    mov x0, x22
    bl _close

    adrp x8, png_readbuf@PAGE
    add x8, x8, png_readbuf@PAGEOFF

    ldrb w2, [x8]
    cmp w2, #137
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #1]
    cmp w2, #'P'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #2]
    cmp w2, #'N'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #3]
    cmp w2, #'G'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #4]
    cmp w2, #13
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #5]
    cmp w2, #10
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #6]
    cmp w2, #26
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #7]
    cmp w2, #10
    b.ne .Lpf_bad_sig

    ldr w10, [x8, #8]
    rev w10, w10
    cmp w10, #13
    b.ne .Lpf_bad_sig

    ldrb w2, [x8, #12]
    cmp w2, #'I'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #13]
    cmp w2, #'H'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #14]
    cmp w2, #'D'
    b.ne .Lpf_bad_sig
    ldrb w2, [x8, #15]
    cmp w2, #'R'
    b.ne .Lpf_bad_sig

    ldr w11, [x8, #16]
    rev w11, w11
    ldr w12, [x8, #20]
    rev w12, w12
    ldrb w13, [x8, #24]
    ldrb w14, [x8, #25]
    ldrb w15, [x8, #28]

    mov x0, x20
    mov x1, x21
    adrp x2, png_fmt@PAGE
    add x2, x2, png_fmt@PAGEOFF
    mov w3, w11
    mov w4, w12
    mov w5, w13
    mov w6, w14
    mov w7, w15
    bl _snprintf

    mov x0, xzr
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #64
    ret

.Lpf_bad_read:
    mov x0, x22
    bl _close
.Lpf_bad_sig:
    mov x0, #-1
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #64
    ret

.Lpf_fail:
    mov x0, #-1
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #64
    ret
