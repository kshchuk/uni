/* Directory listing, path utilities and file metadata for the GUI (variant 4).
 *
 * All functions follow the AAPCS64 ABI: every callee-saved register
 * (x19..x28) written inside the body is preserved on the stack.
 */
    .text
    .align 2

    .equ MAX_ENTRIES, 512
    .equ ENTRY_NAME_LEN, 256
    .equ ENTRY_OFF_ISDIR, 256
    .equ ENTRY_SIZE, 264
    .equ DIRENT_OFF_NAME, 21

    /* macOS ARM64 struct stat (64-bit inode layout) offsets */
    .equ STAT_OFF_MODE, 4
    .equ STAT_OFF_NLINK, 6
    .equ STAT_OFF_INO, 8
    .equ STAT_OFF_UID, 16
    .equ STAT_OFF_GID, 20
    .equ STAT_OFF_ATIMESEC, 32
    .equ STAT_OFF_MTIMESEC, 48
    .equ STAT_OFF_CTIMESEC, 64
    .equ STAT_OFF_BTIMESEC, 80
    .equ STAT_OFF_SIZE, 96
    .equ STAT_SIZE, 160             /* >= sizeof(struct stat) */

    .extern _opendir
    .extern _readdir
    .extern _closedir
    .extern _lstat
    .extern _strcmp
    .extern _strcasecmp
    .extern _strlen
    .extern _qsort
    .extern _localtime_r
    .extern _strftime
    .extern _path_join
    .extern _pfs_str_append
    .extern _pfs_u32_append
    .extern _pfs_u64_append

    .bss
    .align 4
    .globl _g_entries
_g_entries:
    .space MAX_ENTRIES * ENTRY_SIZE
    .globl _g_entry_count
_g_entry_count:
    .space 8

    .section __TEXT,__cstring,cstring_literals
ext_png:
    .asciz ".png"
ext_jpg:
    .asciz ".jpg"
ext_jpeg:
    .asciz ".jpeg"
time_fmt:
    .asciz "%Y-%m-%d %H:%M:%S"

    .text

    /*
     * int dir_cmp(const void *a, const void *b);
     * Directories before files, then lexicographic name.
     */
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
    bl _strcmp
    ldp x29, x30, [sp], #16
    ret

    /*
     * int fs_list_dir(const char *path);
     * Populates g_entries / g_entry_count; returns entry count, -1 on failure.
     */
    .globl _fs_list_dir
_fs_list_dir:
    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]

    mov x25, x0                    /* original path */

    adrp x9, _g_entry_count@PAGE
    add x9, x9, _g_entry_count@PAGEOFF
    str xzr, [x9]

    /* fullpath[1024] + struct stat (~160) + pad -> 1200 bytes */
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
    add x23, x24, #DIRENT_OFF_NAME /* const char *name */

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
    add x1, sp, #1024              /* struct stat */
    bl _lstat
    cbnz x0, .Lrd

    add x4, sp, #1024
    ldr w4, [x4, #STAT_OFF_MODE]
    and w6, w4, #0xf000
    mov w7, #0x4000                /* S_IFDIR */
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
    add x14, x12, x14              /* entry row */

    /* Copy name (<= ENTRY_NAME_LEN-1 bytes) + NUL */
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

    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lld_fail_noclose:
    add sp, sp, #1200
    mov x0, #-1
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

    /*
     * void path_parent_inplace(char *path);
     * Strips the last path component. "/x" -> "/", "/" -> "/".
     */
    .globl _path_parent_inplace
_path_parent_inplace:
    stp x29, x30, [sp, #-32]!
    mov x29, sp
    str x19, [sp, #16]
    mov x19, x0

    bl _strlen
    cmp x0, #1
    b.ls .Lpp_done

    sub x10, x0, #1
.Lpp_loop:
    ldrb w11, [x19, x10]
    cmp w11, #'/'
    b.ne .Lpp_dec
    cmp x10, xzr
    b.eq .Lpp_at_root
    strb wzr, [x19, x10]
    b .Lpp_done
.Lpp_at_root:
    strb wzr, [x19, #1]
    b .Lpp_done
.Lpp_dec:
    subs x10, x10, #1
    b.hs .Lpp_loop

.Lpp_done:
    ldr x19, [sp, #16]
    ldp x29, x30, [sp], #32
    ret

    /*
     * int fs_count_jpg_png(const char *dirpath);
     * Counts regular files with .jpg / .jpeg / .png (case-insensitive) extensions.
     */
    .globl _fs_count_jpg_png
_fs_count_jpg_png:
    stp x29, x30, [sp, #-96]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]

    mov x25, x0                    /* dir path */
    mov x22, xzr                   /* counter */

    sub sp, sp, #1200

    mov x0, x25
    bl _opendir
    cbz x0, .Lcjp_fail
    mov x24, x0                    /* DIR* */

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
    mov w6, #0x8000                /* S_IFREG */
    cmp w5, w6
    b.ne .Lcjp_rd

    mov x0, x21
    bl _strlen
    mov x19, x0                    /* name length */

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
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lcjp_fail:
    add sp, sp, #1200
    mov x0, xzr
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

    /*
     * long long pfs_file_size(const char *path);
     * Returns st_size via lstat(); -1 on failure.
     */
    .globl _pfs_file_size
_pfs_file_size:
    stp x29, x30, [sp, #-32]!
    mov x29, sp

    sub sp, sp, #STAT_SIZE
    mov x1, sp
    bl _lstat
    cbnz x0, .Lfsz_fail

    ldr x0, [sp, #STAT_OFF_SIZE]
    add sp, sp, #STAT_SIZE
    ldp x29, x30, [sp], #32
    ret

.Lfsz_fail:
    add sp, sp, #STAT_SIZE
    mov x0, #-1
    ldp x29, x30, [sp], #32
    ret

    /*
     * int pfs_file_mtime_iso(const char *path, char *buf, size_t buflen);
     * On success writes "YYYY-MM-DD HH:MM:SS" into buf and returns 0.
     * Returns -1 on lstat/localtime_r/strftime failure.
     */
    .globl _pfs_file_mtime_iso
_pfs_file_mtime_iso:
    cbz x1, .Lmti_arg_fail
    cbz x2, .Lmti_arg_fail

    stp x29, x30, [sp, #-48]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]

    mov x19, x1                    /* buf */
    mov x20, x2                    /* buflen */

    /* Stack: struct stat + struct tm + pad = 160 + 64 = 224 */
    sub sp, sp, #224

    /* lstat(path, &stat_buf) */
    mov x1, sp                     /* &stat */
    bl _lstat
    cbnz x0, .Lmti_fail

    /* localtime_r(&mtime_sec, &tm) */
    add x0, sp, #STAT_OFF_MTIMESEC
    add x1, sp, #STAT_SIZE         /* &tm lives after stat */
    bl _localtime_r
    cbz x0, .Lmti_fail

    /* strftime(buf, buflen, "%Y-...", &tm) */
    mov x0, x19
    mov x1, x20
    adrp x2, time_fmt@PAGE
    add x2, x2, time_fmt@PAGEOFF
    add x3, sp, #STAT_SIZE
    bl _strftime
    cbz x0, .Lmti_fail

    add sp, sp, #224
    mov x0, #0
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #48
    ret

.Lmti_fail:
    add sp, sp, #224
    strb wzr, [x19]
    mov x0, #-1
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #48
    ret

.Lmti_arg_fail:
    mov x0, #-1
    ret

    /* ---- Rich metadata formatter ------------------------------------- */

    .section __DATA,__const
    .align 3
ffm_typetbl:
    .byte '?','p','c','?','d','?','b','?','-','?','l','?','s','?','?','?'
ffm_perm_tab:
    /* (bit index, char-if-set) pairs for rwxrwxrwx */
    .byte 8, 'r', 7, 'w', 6, 'x'
    .byte 5, 'r', 4, 'w', 3, 'x'
    .byte 2, 'r', 1, 'w', 0, 'x'

    .section __TEXT,__cstring,cstring_literals
ffm_s_perm:
    .asciz "Permissions: "
ffm_s_links:
    .asciz "\nLinks: "
ffm_s_owner:
    .asciz "\nOwner: "
ffm_s_colon:
    .asciz ":"
ffm_s_inode:
    .asciz "\nInode: "
ffm_s_acc:
    .asciz "\nAccessed: "
ffm_s_mod:
    .asciz "\nModified: "
ffm_s_crt:
    .asciz "\nCreated: "

    .text
    .align 2

    /*
     * int pfs_format_fullmeta(const char *path, char *buf, size_t buflen);
     * Writes:
     *   Permissions: -rwxr-xr-x
     *   Links: N
     *   Owner: UID:GID
     *   Inode: N
     *   Accessed: YYYY-MM-DD HH:MM:SS
     *   Modified: YYYY-MM-DD HH:MM:SS
     *   Created:  YYYY-MM-DD HH:MM:SS
     * Returns 0 on success, -1 on lstat failure.
     */
    .globl _pfs_format_fullmeta
_pfs_format_fullmeta:
    cbz x1, .Lffm_argfail
    cbz x2, .Lffm_argfail

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

    /* stat(160) + tm(64) + time_buf(32) = 256 */
    sub sp, sp, #256
    mov x22, sp                    /* &stat */

    mov x1, x22
    bl _lstat
    cbnz x0, .Lffm_fail

    /* "Permissions: " */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_perm@PAGE
    add x2, x2, ffm_s_perm@PAGEOFF
    bl _pfs_str_append
    mov x21, x0

    /* Type char from high nibble of mode */
    ldrh w23, [x22, #STAT_OFF_MODE]
    lsr w24, w23, #12
    and w24, w24, #0xf
    adrp x4, ffm_typetbl@PAGE
    add x4, x4, ffm_typetbl@PAGEOFF
    ldrb w10, [x4, x24]
    cmp x21, x20
    b.hs .Lffm_type_skip
    strb w10, [x21], #1
.Lffm_type_skip:

    /* 9 permission chars via (bit, char) table */
    adrp x5, ffm_perm_tab@PAGE
    add x5, x5, ffm_perm_tab@PAGEOFF
    mov w11, #9
.Lffm_perm_loop:
    ldrb w12, [x5], #1            /* bit index */
    ldrb w13, [x5], #1            /* char-if-set */
    mov w8, #1
    lsl w8, w8, w12
    and w8, w23, w8
    cbnz w8, .Lffm_perm_set
    mov w13, #'-'
.Lffm_perm_set:
    cmp x21, x20
    b.hs .Lffm_perm_next
    strb w13, [x21], #1
.Lffm_perm_next:
    subs w11, w11, #1
    b.ne .Lffm_perm_loop

    /* "\nLinks: " */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_links@PAGE
    add x2, x2, ffm_s_links@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    ldrh w2, [x22, #STAT_OFF_NLINK]
    mov x0, x21
    mov x1, x20
    bl _pfs_u32_append
    mov x21, x0

    /* "\nOwner: UID:GID" */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_owner@PAGE
    add x2, x2, ffm_s_owner@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    ldr w2, [x22, #STAT_OFF_UID]
    mov x0, x21
    mov x1, x20
    bl _pfs_u32_append
    mov x21, x0
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_colon@PAGE
    add x2, x2, ffm_s_colon@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    ldr w2, [x22, #STAT_OFF_GID]
    mov x0, x21
    mov x1, x20
    bl _pfs_u32_append
    mov x21, x0

    /* "\nInode: N" */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_inode@PAGE
    add x2, x2, ffm_s_inode@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    ldr x2, [x22, #STAT_OFF_INO]
    mov x0, x21
    mov x1, x20
    bl _pfs_u64_append
    mov x21, x0

    /* "\nAccessed: <iso>" */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_acc@PAGE
    add x2, x2, ffm_s_acc@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    mov w9, #STAT_OFF_ATIMESEC
    bl .Lffm_append_time

    /* "\nModified: <iso>" */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_mod@PAGE
    add x2, x2, ffm_s_mod@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    mov w9, #STAT_OFF_MTIMESEC
    bl .Lffm_append_time

    /* "\nCreated: <iso>" */
    mov x0, x21
    mov x1, x20
    adrp x2, ffm_s_crt@PAGE
    add x2, x2, ffm_s_crt@PAGEOFF
    bl _pfs_str_append
    mov x21, x0
    mov w9, #STAT_OFF_BTIMESEC
    bl .Lffm_append_time

    strb wzr, [x21]

    add sp, sp, #256
    mov x0, #0
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lffm_fail:
    add sp, sp, #256
    strb wzr, [x19]
    mov x0, #-1
    ldp x27, x28, [sp, #80]
    ldp x25, x26, [sp, #64]
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

.Lffm_argfail:
    mov x0, #-1
    ret

    /*
     * Internal helper: append ISO time for stat field @ w9 offset.
     * Uses x22=&stat (with tm@+160, tmp@+224), updates x21 (cursor),
     * bounded by x20 (end). Leaves x22,x21,x20 intact on failure.
     */
.Lffm_append_time:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    add x0, x22, x9
    add x1, x22, #160
    bl _localtime_r
    cbz x0, .Lffm_at_done
    add x0, x22, #224
    mov x1, #32
    adrp x2, time_fmt@PAGE
    add x2, x2, time_fmt@PAGEOFF
    add x3, x22, #160
    bl _strftime
    cbz x0, .Lffm_at_done
    mov x0, x21
    mov x1, x20
    add x2, x22, #224
    bl _pfs_str_append
    mov x21, x0
.Lffm_at_done:
    ldp x29, x30, [sp], #16
    ret
