/*
 * String output and timespec formatting (birthtime / mtime).
 */
    .text
    .align 2

    .extern _write
    .extern _localtime_r
    .extern _strftime

    /* void render_write_z(int fd, const char *s); */
    .globl _render_write_z
_render_write_z:
    stp x29, x30, [sp, #-32]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    mov x19, x0
    mov x20, x1
0:
    ldrb w2, [x20], #1
    cbz w2, 1f
    sub x20, x20, #1
    mov x0, x19
    mov x1, x20
    mov x2, #1
    bl _write
    add x20, x20, #1
    b 0b
1:
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #32
    ret

    /*
     * size_t render_fmt_timespec_to_buf(int64_t tv_sec, int64_t tv_nsec,
     *                                   char *buf, size_t buflen);
     */
    .globl _render_fmt_timespec_to_buf
_render_fmt_timespec_to_buf:
    stp x29, x30, [sp, #-192]!
    mov x29, sp
    stp x19, x22, [sp, #16]

    mov x19, x2                    /* buf */
    mov x20, x3                    /* buflen */
    mov x21, x0                    /* tv_sec */

    sub sp, sp, #128               /* struct tm + time_t + alignment */

    str x21, [sp, #64]             /* time_t */
    add x0, sp, #64
    mov x1, sp
    bl _localtime_r
    cbz x0, .Lfmt_fail

    mov x0, x19
    mov x1, x20
    adrp x2, fmt_ts@PAGE
    add x2, x2, fmt_ts@PAGEOFF
    mov x3, sp
    bl _strftime
    cbz x0, .Lfmt_fail

    mov x22, x0
    mov x0, x22
    add sp, sp, #128
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #192
    ret
.Lfmt_fail:
    mov x0, #0
    add sp, sp, #128
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #192
    ret

    .section __TEXT,__cstring,cstring_literals
fmt_ts:
    .asciz "%Y-%m-%d %H:%M:%S"
