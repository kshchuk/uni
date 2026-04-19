/*
 * Directory listing, path_join, qsort (directories first).
 */
    .text
    .align 2

    .equ MAX_ENTRIES, 512
    .equ ENTRY_NAME_LEN, 256
    .equ ENTRY_OFF_ISDIR, 256
    .equ ENTRY_SIZE, 264
    .equ DIRENT_OFF_NAME, 21

    .extern _opendir
    .extern _readdir
    .extern _closedir
    .extern _lstat
    .extern _strcmp
    .extern _strcasecmp
    .extern _strlen
    .extern _snprintf
    .extern _qsort

    .equ STAT_OFF_MODE, 4

    .bss
    .align 4
    .globl _g_entries
_g_entries:
    .space MAX_ENTRIES * ENTRY_SIZE
    .globl _g_entry_count
_g_entry_count:
    .space 8

    .section __TEXT,__cstring,cstring_literals
slash_str:
    .asciz "/"
fmt_join:
    .asciz "%s/%s"
fmt_root_name:
    .asciz "/%s"

    .text

    .globl _path_join
_path_join:
    stp x29, x30, [sp, #-48]!
    mov x29, sp
    stp x19, x22, [sp, #16]

    mov x19, x0                    /* out */
    mov x20, x1                    /* outsiz */
    mov x21, x2                    /* base */
    mov x22, x3                    /* name */

    mov x0, x21
    adrp x1, slash_str@PAGE
    add x1, x1, slash_str@PAGEOFF
    bl _strcmp
    cbnz x0, .Lpj_pair

    mov x0, x19
    mov x1, x20
    adrp x2, fmt_root_name@PAGE
    add x2, x2, fmt_root_name@PAGEOFF
    mov x3, x22
    bl _snprintf
    b .Lpj_end

.Lpj_pair:
    mov x0, x19
    mov x1, x20
    adrp x2, fmt_join@PAGE
    add x2, x2, fmt_join@PAGEOFF
    mov x3, x21
    mov x4, x22
    bl _snprintf

.Lpj_end:
    ldp x19, x22, [sp, #16]
    ldp x29, x30, [sp], #48
    ret

    .globl _dir_cmp
_dir_cmp:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    ldrb w2, [x0, #ENTRY_OFF_ISDIR]
    ldrb w3, [x1, #ENTRY_OFF_ISDIR]

    cmp w2, #1
    b.ne .La_nd
    cmp w3, #1
    b.eq .Lcmp_names
    mov x0, #-1
    ldp x29, x30, [sp], #16
    ret

.La_nd:
    cmp w3, #1
    b.ne .Lcmp_names
    mov x0, #1
    ldp x29, x30, [sp], #16
    ret

.Lcmp_names:
    mov x0, x0
    mov x1, x1
    bl _strcmp
    ldp x29, x30, [sp], #16
    ret

    /*
     * int fs_list_dir(const char *path);
     */
    .globl _fs_list_dir
_fs_list_dir:
    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x26, [sp, #16]

    mov x25, x0                    /* original path ptr */

    adrp x9, _g_entry_count@PAGE
    add x9, x9, _g_entry_count@PAGEOFF
    str xzr, [x9]

    /* Stack: fullpath[1024] + struct stat (~144), 16-byte aligned */
    sub sp, sp, #1200

    mov x0, x25
    bl _opendir
    cbz x0, .Lld_fail_noclose
    mov x26, x0                    /* DIR* */

.Lrd:
    mov x0, x26
    bl _readdir
    cbz x0, .Lrd_done

    mov x24, x0                    /* dirent* */
    add x23, x24, #DIRENT_OFF_NAME /* char* name */

    ldrb w4, [x23]
    cmp w4, #'.'
    b.ne .Lnm_ok
    ldrb w5, [x23, #1]
    cbz w5, .Lrd                    /* "." */
    cmp w5, #'.'
    b.ne .Lnm_ok
    ldrb w5, [x23, #2]
    cbz w5, .Lrd                    /* ".." */
.Lnm_ok:

    mov x0, sp                     /* fullpath */
    mov x1, #1024
    mov x2, x25
    mov x3, x23
    bl _path_join

    mov x0, sp
    add x1, sp, #1024
    bl _lstat
    cbnz x0, .Lrd

    add x4, sp, #1024
    ldr w4, [x4, #STAT_OFF_MODE]

    /* S_IFDIR: (mode & S_IFMT) == S_IFDIR */
    and w6, w4, #0xf000
    mov w7, #0x4000
    cmp w6, w7
    cset w8, eq

    adrp x9, _g_entry_count@PAGE
    add x9, x9, _g_entry_count@PAGEOFF
    ldr x10, [x9]
    cmp x10, #MAX_ENTRIES
    b.hs .Lrd_done

    mov x11, #ENTRY_SIZE
    madd x14, x10, x11, xzr
    adrp x12, _g_entries@PAGE
    add x12, x12, _g_entries@PAGEOFF
    add x14, x12, x14

    /* Copy name, max ENTRY_NAME_LEN-1 chars + NUL */
    mov x15, x23
    mov x16, x14
    mov x17, #(ENTRY_NAME_LEN - 1)
.Lcp:
    cbz x17, .Lcp_trunc
    ldrb w0, [x15], #1
    strb w0, [x16], #1
    cbz w0, .Lafter_cp
    sub x17, x17, #1
    b .Lcp
.Lcp_trunc:
    strb wzr, [x16]
    b .Lafter_cp
.Lafter_cp:

    strb w8, [x14, #ENTRY_OFF_ISDIR]

    add x10, x10, #1
    str x10, [x9]

    b .Lrd

.Lrd_done:
    mov x0, x26
    bl _closedir

    add sp, sp, #1200

    adrp x2, _g_entry_count@PAGE
    add x2, x2, _g_entry_count@PAGEOFF
    ldr x1, [x2]
    cbz x1, .Lld_retct

    adrp x0, _g_entries@PAGE
    add x0, x0, _g_entries@PAGEOFF
    mov x2, #ENTRY_SIZE
    adrp x3, _dir_cmp@PAGE
    add x3, x3, _dir_cmp@PAGEOFF
    bl _qsort

.Lld_retct:
    adrp x0, _g_entry_count@PAGE
    add x0, x0, _g_entry_count@PAGEOFF
    ldr x0, [x0]

    ldp x19, x26, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lld_fail_noclose:
    add sp, sp, #1200
    mov x0, #-1
    ldp x19, x26, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

    .section __TEXT,__cstring,cstring_literals
ext_png:
    .asciz ".png"
ext_jpg:
    .asciz ".jpg"
ext_jpeg:
    .asciz ".jpeg"

    .text

    /*
     * void path_parent_inplace(char *path);
     */
    .globl _path_parent_inplace
_path_parent_inplace:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov x19, x0

    mov x0, x19
    bl _strlen
    cmp x0, #1
    b.ls .Lpp_done                /* len <= 1 -> "/" */

    mov x20, x0                    /* len */
    sub x21, x20, #1             /* i = len-1 */

.Lpp_loop:
    ldrb w4, [x19, x21]
    cmp w4, #'/'
    b.ne .Lpp_dec
    cmp x21, xzr
    b.eq .Lpp_at_root
    strb wzr, [x19, x21]
    b .Lpp_done
.Lpp_at_root:
    strb wzr, [x19, #1]
    b .Lpp_done
.Lpp_dec:
    subs x21, x21, #1
    b.hs .Lpp_loop

.Lpp_done:
    ldp x29, x30, [sp], #16
    ret

    /*
     * int fs_count_jpg_png(const char *dirpath);
     * Count regular files with .jpg / .jpeg / .png extensions (case-insensitive).
     */
    .globl _fs_count_jpg_png
_fs_count_jpg_png:
    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x24, [sp, #16]

    mov x25, x0
    mov x22, xzr                   /* counter */

    sub sp, sp, #1200

    mov x0, x25
    bl _opendir
    cbz x0, .Lcjp_fail
    mov x24, x0

.Lcjp_rd:
    mov x0, x24
    bl _readdir
    cbz x0, .Lcjp_done

    mov x23, x0
    add x21, x23, #DIRENT_OFF_NAME

    ldrb w4, [x21]
    cmp w4, #'.'
    b.ne .Lcjp_nm
    ldrb w5, [x21, #1]
    cbz w5, .Lcjp_rd
    cmp w5, #'.'
    b.ne .Lcjp_nm
    ldrb w5, [x21, #2]
    cbz w5, .Lcjp_rd
.Lcjp_nm:

    mov x0, sp
    mov x1, #1024
    mov x2, x25
    mov x3, x21
    bl _path_join

    mov x0, sp
    add x1, sp, #1024
    bl _lstat
    cbnz x0, .Lcjp_rd

    add x2, sp, #1024
    ldr w4, [x2, #STAT_OFF_MODE]
    and w5, w4, #0xf000
    mov w6, #0x8000               /* S_IFREG */
    cmp w5, w6
    b.ne .Lcjp_rd

    mov x0, x21
    bl _strlen
    mov x19, x0                    /* len */

    cmp x19, #4
    b.lo .Lcjp_rd

    add x0, x21, x19
    sub x0, x0, #4
    adrp x1, ext_png@PAGE
    add x1, x1, ext_png@PAGEOFF
    bl _strcasecmp
    cbz x0, .Lcjp_inc

    add x0, x21, x19
    sub x0, x0, #4
    adrp x1, ext_jpg@PAGE
    add x1, x1, ext_jpg@PAGEOFF
    bl _strcasecmp
    cbz x0, .Lcjp_inc

    cmp x19, #5
    b.lo .Lcjp_rd
    add x0, x21, x19
    sub x0, x0, #5
    adrp x1, ext_jpeg@PAGE
    add x1, x1, ext_jpeg@PAGEOFF
    bl _strcasecmp
    cbnz x0, .Lcjp_rd

.Lcjp_inc:
    add x22, x22, #1
    b .Lcjp_rd

.Lcjp_done:
    mov x0, x24
    bl _closedir
    add sp, sp, #1200
    mov x0, x22
    ldp x19, x24, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lcjp_fail:
    add sp, sp, #1200
    mov x0, xzr
    ldp x19, x24, [sp, #16]
    ldp x29, x30, [sp], #96
    ret
