/* int jpeg_format_info(const char *path, char *buf, size_t buflen);
 *
 * Reads up to 64 KiB from the file, verifies the SOI marker (FF D8),
 * walks JPEG segments looking for a Start-Of-Frame (SOF0..SOF15 except
 * the Huffman/arithmetic variants), extracts:
 *   - sample precision (bits per channel)
 *   - image height / width (big-endian u16)
 *   - component count (1 = greyscale, 3 = YCbCr, 4 = CMYK)
 *   - SOF flavor name (baseline / extended / progressive / lossless /
 *                     differential / other)
 * Then emits:
 *
 *   "JPEG info\n"
 *   "Dimensions: <W> x <H> px\n"
 *   "Precision: <P> bits/ch\n"
 *   "Channels: <N>\n"
 *   "Mode: <flavor>"
 *
 * Returns 0 on success, -1 on any malformed or non-JPEG input.
 * Pure asm; all bounded writes via pfs_str_append / pfs_u32_append.
 */
    .text
    .align 2

    .extern _open
    .extern _read
    .extern _close
    .extern _pfs_str_append
    .extern _pfs_u32_append

    .equ JPG_BUF_LEN, 65536

    .section __TEXT,__cstring,cstring_literals
jpeg_s_header:
    .asciz "JPEG info\nDimensions: "
jpeg_s_x:
    .asciz " x "
jpeg_s_px:
    .asciz " px\nPrecision: "
jpeg_s_bits:
    .asciz " bits/ch\nChannels: "
jpeg_s_mode:
    .asciz "\nMode: "
jpeg_mode_base:
    .asciz "baseline"
jpeg_mode_ext:
    .asciz "extended sequential"
jpeg_mode_prog:
    .asciz "progressive"
jpeg_mode_loss:
    .asciz "lossless"
jpeg_mode_diff:
    .asciz "differential"
jpeg_mode_other:
    .asciz "other"

    .text
    .align 2
    .globl _jpeg_format_info
_jpeg_format_info:
    cbz x0, .Ljpg_argfail
    cbz x1, .Ljpg_argfail
    cbz x2, .Ljpg_argfail

    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]

    mov x19, x1                    /* buf */
    sub x2, x2, #1
    add x20, x1, x2                /* end (reserve NUL) */
    mov x21, x19                   /* cursor */

    /* Local: data[65536] */
    sub sp, sp, #JPG_BUF_LEN
    mov x22, sp                    /* data buffer */

    /* fd = open(path, O_RDONLY, 0) */
    mov x1, #0
    mov x2, #0
    bl _open
    cmn x0, #1
    b.eq .Ljpg_fail
    mov x23, x0                    /* fd */

    /* n = read(fd, data, 65536) */
    mov x0, x23
    mov x1, x22
    mov x2, #JPG_BUF_LEN
    bl _read
    mov x24, x0                    /* bytes read */

    /* close(fd) */
    mov x0, x23
    bl _close

    cmp x24, #4
    b.lt .Ljpg_fail

    /* Check SOI: FF D8 */
    ldrb w4, [x22]
    cmp w4, #0xFF
    b.ne .Ljpg_fail
    ldrb w4, [x22, #1]
    cmp w4, #0xD8
    b.ne .Ljpg_fail

    /* i = 2 */
    mov x25, #2

.Ljpg_next:
    /* need at least 4 bytes for marker + length */
    add x4, x25, #4
    cmp x4, x24
    b.hi .Ljpg_fail

    /* skip any FF fill bytes */
.Ljpg_fill:
    ldrb w4, [x22, x25]
    cmp w4, #0xFF
    b.ne .Ljpg_fail
    add x25, x25, #1
    cmp x25, x24
    b.hs .Ljpg_fail
    ldrb w4, [x22, x25]
    cmp w4, #0xFF
    b.eq .Ljpg_fill

    /* w4 = marker byte, x25 points at it */
    mov w26, w4
    add x25, x25, #1

    /* Markers without payload: 01, D0..D7, D8, D9 */
    cmp w26, #0x01
    b.eq .Ljpg_next
    cmp w26, #0xD8
    b.eq .Ljpg_next
    cmp w26, #0xD9
    b.eq .Ljpg_fail               /* EOI before SOF */
    and w5, w26, #0xF8
    cmp w5, #0xD0
    b.eq .Ljpg_next               /* D0..D7 (RSTn, no payload) */

.Ljpg_has_len:
    /* Need 2 bytes of length */
    add x4, x25, #2
    cmp x4, x24
    b.hi .Ljpg_fail
    ldrb w5, [x22, x25]           /* length high */
    add x4, x25, #1
    ldrb w6, [x22, x4]            /* length low */
    lsl w5, w5, #8
    orr w5, w5, w6                /* segment length (incl. length bytes) */

    /* Is this a SOF we understand?
     *   SOF0..SOF15, except C4 (DHT), C8 (JPG reserved), CC (DAC). */
    and w7, w26, #0xF0
    cmp w7, #0xC0
    b.ne .Ljpg_skip
    cmp w26, #0xC4
    b.eq .Ljpg_skip
    cmp w26, #0xC8
    b.eq .Ljpg_skip
    cmp w26, #0xCC
    b.eq .Ljpg_skip

    /* --- Parse SOF segment ---
     * Layout after marker:
     *   [len_hi len_lo] [precision] [height_hi height_lo]
     *   [width_hi width_lo] [nf]
     * Need len >= 8. Segment payload starts at x25+2.
     */
    cmp w5, #8
    b.lo .Ljpg_fail

    add x7, x25, #2                /* start of body */
    add x4, x7, #6
    cmp x4, x24
    b.hi .Ljpg_fail

    ldrb w27, [x22, x7]            /* precision */

    add x4, x7, #1
    ldrb w5, [x22, x4]
    add x4, x7, #2
    ldrb w6, [x22, x4]
    lsl w5, w5, #8
    orr w28, w5, w6                /* height */

    add x4, x7, #3
    ldrb w5, [x22, x4]
    add x4, x7, #4
    ldrb w6, [x22, x4]
    lsl w5, w5, #8
    orr w5, w5, w6                 /* width */

    /* Move width into a safe callee-saved slot */
    /* Repurpose x24 (bytes read) since we no longer need it. */
    mov w24, w5

    add x4, x7, #5
    ldrb w25, [x22, x4]            /* channel count (reuse x25) */

    /* --- Emit output ---
     * "JPEG info\nDimensions: "
     */
    mov x0, x21
    mov x1, x20
    adrp x2, jpeg_s_header@PAGE
    add x2, x2, jpeg_s_header@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    mov w2, w24                    /* width */
    bl _pfs_u32_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    adrp x2, jpeg_s_x@PAGE
    add x2, x2, jpeg_s_x@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    mov w2, w28                    /* height */
    bl _pfs_u32_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    adrp x2, jpeg_s_px@PAGE
    add x2, x2, jpeg_s_px@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    mov w2, w27                    /* precision */
    bl _pfs_u32_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    adrp x2, jpeg_s_bits@PAGE
    add x2, x2, jpeg_s_bits@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    mov w2, w25                    /* channels */
    bl _pfs_u32_append
    mov x21, x0

    mov x0, x21
    mov x1, x20
    adrp x2, jpeg_s_mode@PAGE
    add x2, x2, jpeg_s_mode@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    /* Select mode string based on original marker (was w26). It was clobbered
     * by the parsing above only inside w5/w6. Re-derive from precision? No —
     * w26 is intact (we kept it untouched). */
    mov x0, x21
    mov x1, x20
    and w4, w26, #0x0F             /* low nibble decides family */
    /* low nibble semantics inside C0..CF (excl. 4,8,C):
     *   0 -> baseline (SOF0)
     *   1 -> extended sequential (SOF1)
     *   2 -> progressive (SOF2)
     *   3 -> lossless  (SOF3)
     *   5,6,7 -> differential sequential/progressive/lossless
     *   9,A,B -> arith-coded sequential/progressive/lossless
     *   D,E,F -> differential arith-coded
     */
    adrp x2, jpeg_mode_other@PAGE
    add x2, x2, jpeg_mode_other@PAGEOFF
    cmp w4, #0
    b.ne .Ljpg_m1
    adrp x2, jpeg_mode_base@PAGE
    add x2, x2, jpeg_mode_base@PAGEOFF
    b .Ljpg_emit_mode
.Ljpg_m1:
    cmp w4, #1
    b.ne .Ljpg_m2
    adrp x2, jpeg_mode_ext@PAGE
    add x2, x2, jpeg_mode_ext@PAGEOFF
    b .Ljpg_emit_mode
.Ljpg_m2:
    cmp w4, #2
    b.ne .Ljpg_m3
    adrp x2, jpeg_mode_prog@PAGE
    add x2, x2, jpeg_mode_prog@PAGEOFF
    b .Ljpg_emit_mode
.Ljpg_m3:
    cmp w4, #3
    b.ne .Ljpg_mdiff_chk
    adrp x2, jpeg_mode_loss@PAGE
    add x2, x2, jpeg_mode_loss@PAGEOFF
    b .Ljpg_emit_mode
.Ljpg_mdiff_chk:
    /* 5,6,7,D,E,F treat as differential */
    cmp w4, #5
    b.lt .Ljpg_emit_mode
    cmp w4, #7
    b.le .Ljpg_mdiff_set
    cmp w4, #0xD
    b.lt .Ljpg_emit_mode
    cmp w4, #0xF
    b.gt .Ljpg_emit_mode
.Ljpg_mdiff_set:
    adrp x2, jpeg_mode_diff@PAGE
    add x2, x2, jpeg_mode_diff@PAGEOFF
.Ljpg_emit_mode:
    bl _pfs_str_append
    mov x21, x0

    strb wzr, [x21]

    add sp, sp, #JPG_BUF_LEN
    mov x0, #0
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Ljpg_skip:
    /* Advance past this segment: new i = (start of length) + length */
    add x25, x25, x5
    cmp x25, x24
    b.hs .Ljpg_fail
    b .Ljpg_next

.Ljpg_fail:
    strb wzr, [x19]
    add sp, sp, #JPG_BUF_LEN
    mov x0, #-1
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Ljpg_argfail:
    mov x0, #-1
    ret
