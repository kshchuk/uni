/* void path_join(char *out, size_t outsiz, const char *base, const char *name);
 * Behaviour matches the previous C version:
 *   base == "/"  -> "/name"
 *   otherwise    -> "base/name"
 * Output is NUL-terminated and truncated to outsiz-1 bytes.
 * No external calls; all registers used are caller-saved.
 */
    .text
    .align 2
    .globl _path_join
_path_join:
    cbz x0, .Lpj_ret
    cbz x1, .Lpj_ret
    cbz x2, .Lpj_ret
    cbz x3, .Lpj_ret

    sub x1, x1, #1                 /* remaining = outsiz - 1 (reserve NUL) */
    mov x6, x0                     /* cursor */

    /* base == "/" ? */
    ldrb w4, [x2]
    cmp w4, #'/'
    b.ne .Lpj_copybase
    ldrb w5, [x2, #1]
    cbz w5, .Lpj_sep_only

.Lpj_copybase:
    cbz x1, .Lpj_terminate
    ldrb w7, [x2], #1
    cbz w7, .Lpj_addsep
    strb w7, [x6], #1
    sub x1, x1, #1
    b .Lpj_copybase

.Lpj_addsep:
    cbz x1, .Lpj_terminate
    mov w7, #'/'
    strb w7, [x6], #1
    sub x1, x1, #1
    b .Lpj_copyname

.Lpj_sep_only:
    cbz x1, .Lpj_terminate
    mov w7, #'/'
    strb w7, [x6], #1
    sub x1, x1, #1

.Lpj_copyname:
    cbz x1, .Lpj_terminate
    ldrb w7, [x3], #1
    cbz w7, .Lpj_terminate
    strb w7, [x6], #1
    sub x1, x1, #1
    b .Lpj_copyname

.Lpj_terminate:
    strb wzr, [x6]
.Lpj_ret:
    ret
