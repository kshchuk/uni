#ifndef PFS_CORE_H
#define PFS_CORE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PFS_ENTRY_NAME_LEN 256
#define PFS_ENTRY_OFF_ISDIR 256
#define PFS_ENTRY_SIZE 264

extern unsigned char g_entries[];
extern uint64_t g_entry_count;

/* fills g_entries from directory path; returns count or -1 on error. */
int fs_list_dir(const char *path);
/* builds "base/name" into out, truncating safely to outsiz-1 with NUL. */
void path_join(char *out, size_t outsiz, const char *base, const char *name);
/* Rewrites path to its parent directory in place (root stays "/"). */
void path_parent_inplace(char *path);
/* Counts regular files with .jpg/.jpeg/.png extension in dirpath. */
int fs_count_jpg_png(const char *dirpath);
/* parses PNG IHDR and writes a short human-readable summary to buf. */
int png_format_ihdr_info(const char *path, char *buf, size_t buflen);
/* Parses JPEG SOF info and writes a short human-readable summary to buf. */
int jpeg_format_info(const char *path, char *buf, size_t buflen);

/* File metadata helpers (asm): */
/* Returns file size from lstat(), or -1 on failure. */
long long pfs_file_size(const char *path);
/* Writes file mtime as "YYYY-MM-DD HH:MM:SS"; returns 0/-1. */
int pfs_file_mtime_iso(const char *path, char *buf, size_t buflen);
/* Writes rich metadata block (mode, owner, inode, timestamps); 0/-1. */
int pfs_format_fullmeta(const char *path, char *buf, size_t buflen);

#ifdef __cplusplus
}
#endif

#endif
