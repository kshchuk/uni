/* int png_format_ihdr_info(const char *path, char *buf, size_t buflen);
 *
 * Opens the PNG, reads up to 8 KiB, validates the 8-byte signature and the
 * IHDR chunk (length 13, type "IHDR"), then writes a human-readable preview:
 *
 *   "PNG IHDR preview\n"
 *   "Dimensions: <W> x <H> px\n"
 *   "Bit depth: <bd>\n"
 *   "Color type: <ct>\n"
 *   "Interlace: <il>"
 *
 * Returns 0 on success, -1 on any failure (open/read/signature/IHDR).
 * Pure asm; number formatting via pfs_u32_append.
 */
    .text
    .align 2

    .extern _open
    .extern _read
    .extern _close
    .extern _pfs_str_append
    .extern _pfs_u32_append

    .section __DATA,__const
    .align 3
_png_signature:
    .byte 137, 80, 78, 71, 13, 10, 26, 10

    .section __TEXT,__cstring,cstring_literals
_png_s_header:
    .asciz "PNG IHDR preview\nDimensions: "
_png_s_x:
    .asciz " x "
_png_s_px:
    .asciz " px\nBit depth: "
_png_s_color:
    .asciz "\nColor type: "
_png_s_interlace:
    .asciz "\nInterlace: "

    .text
    .align 2
    .globl _png_format_ihdr_info
_png_format_ihdr_info:
    /* x0 = path, x1 = buf, x2 = buflen */
    cbz x0, .Lpng_arg_fail
    cbz x1, .Lpng_arg_fail
    cbz x2, .Lpng_arg_fail

    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]

    mov x19, x1                    /* buf */
    mov x20, x2                    /* buflen */
    sub sp, sp, #8192
    mov x21, sp                    /* data[8192] */

    /* fd = open(path, O_RDONLY=0, 0) */
    mov x1, #0
    mov x2, #0
    bl _open
    cmn x0, #1
    b.eq .Lpng_fail
    mov x22, x0                    /* fd */

    /* n = read(fd, data, 8192) */
    mov x0, x22
    mov x1, x21
    mov x2, #8192
    bl _read
    mov x23, x0                    /* n */

    /* close(fd) */
    mov x0, x22
    bl _close

    cmp x23, #33
    b.lt .Lpng_fail

    /* Signature check */
    adrp x4, _png_signature@PAGE
    add x4, x4, _png_signature@PAGEOFF
    mov x5, #0
.Lpng_sig:
    ldrb w6, [x21, x5]
    ldrb w7, [x4, x5]
    cmp w6, w7
    b.ne .Lpng_fail
    add x5, x5, #1
    cmp x5, #8
    b.lo .Lpng_sig

    /* Chunk length (big-endian 32) at offset 8 must be 13 */
    ldrb w4, [x21, #8]
    ldrb w5, [x21, #9]
    ldrb w6, [x21, #10]
    ldrb w7, [x21, #11]
    cbnz w4, .Lpng_fail
    cbnz w5, .Lpng_fail
    cbnz w6, .Lpng_fail
    cmp w7, #13
    b.ne .Lpng_fail

    /* Chunk type "IHDR" at offset 12..15 */
    ldrb w4, [x21, #12]
    cmp w4, #'I'
    b.ne .Lpng_fail
    ldrb w4, [x21, #13]
    cmp w4, #'H'
    b.ne .Lpng_fail
    ldrb w4, [x21, #14]
    cmp w4, #'D'
    b.ne .Lpng_fail
    ldrb w4, [x21, #15]
    cmp w4, #'R'
    b.ne .Lpng_fail

    /* Width @ 16..19 (big-endian u32) */
    ldrb w4, [x21, #16]
    ldrb w5, [x21, #17]
    ldrb w6, [x21, #18]
    ldrb w7, [x21, #19]
    lsl w4, w4, #24
    orr w4, w4, w5, lsl #16
    orr w4, w4, w6, lsl #8
    orr w24, w4, w7                /* width */

    /* Height @ 20..23 */
    ldrb w4, [x21, #20]
    ldrb w5, [x21, #21]
    ldrb w6, [x21, #22]
    ldrb w7, [x21, #23]
    lsl w4, w4, #24
    orr w4, w4, w5, lsl #16
    orr w4, w4, w6, lsl #8
    orr w25, w4, w7                /* height */

    /* bit depth / color type / interlace remain in data[21+]; read when writing */

    /* cursor x26, end x27 */
    sub x27, x20, #1
    add x27, x19, x27              /* end (reserve NUL) */
    mov x26, x19                   /* cursor */

    /* "PNG IHDR preview\nDimensions: " */
    mov x0, x26
    mov x1, x27
    adrp x2, _png_s_header@PAGE
    add x2, x2, _png_s_header@PAGEOFF
    bl _pfs_str_append
    mov x26, x0

    /* width */
    mov x0, x26
    mov x1, x27
    mov w2, w24
    bl _pfs_u32_append
    mov x26, x0

    /* " x " */
    mov x0, x26
    mov x1, x27
    adrp x2, _png_s_x@PAGE
    add x2, x2, _png_s_x@PAGEOFF
    bl _pfs_str_append
    mov x26, x0

    /* height */
    mov x0, x26
    mov x1, x27
    mov w2, w25
    bl _pfs_u32_append
    mov x26, x0

    /* " px\nBit depth: " */
    mov x0, x26
    mov x1, x27
    adrp x2, _png_s_px@PAGE
    add x2, x2, _png_s_px@PAGEOFF
    bl _pfs_str_append
    mov x26, x0

    /* bit depth (byte @ 24) */
    mov x0, x26
    mov x1, x27
    ldrb w2, [x21, #24]
    bl _pfs_u32_append
    mov x26, x0

    /* "\nColor type: " */
    mov x0, x26
    mov x1, x27
    adrp x2, _png_s_color@PAGE
    add x2, x2, _png_s_color@PAGEOFF
    bl _pfs_str_append
    mov x26, x0

    /* color type (byte @ 25) */
    mov x0, x26
    mov x1, x27
    ldrb w2, [x21, #25]
    bl _pfs_u32_append
    mov x26, x0

    /* "\nInterlace: " */
    mov x0, x26
    mov x1, x27
    adrp x2, _png_s_interlace@PAGE
    add x2, x2, _png_s_interlace@PAGEOFF
    bl _pfs_str_append
    mov x26, x0

    /* interlace (byte @ 28) */
    mov x0, x26
    mov x1, x27
    ldrb w2, [x21, #28]
    bl _pfs_u32_append
    mov x26, x0

    /* NUL terminate */
    strb wzr, [x26]

    mov x0, #0
    b .Lpng_epilogue

.Lpng_fail:
    /* Put an empty string in buf for safety, return -1 */
    strb wzr, [x19]
    mov x0, #-1

.Lpng_epilogue:
    add sp, sp, #8192
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lpng_arg_fail:
    mov x0, #-1
    ret
