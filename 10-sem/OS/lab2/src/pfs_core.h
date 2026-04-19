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

int fs_list_dir(const char *path);
void path_join(char *out, size_t outsiz, const char *base, const char *name);
void path_parent_inplace(char *path);
int fs_count_jpg_png(const char *dirpath);
int png_format_ihdr_info(const char *path, char *buf, size_t buflen);
int jpeg_format_info(const char *path, char *buf, size_t buflen);

/* File metadata helpers (asm): */
long long pfs_file_size(const char *path);
int pfs_file_mtime_iso(const char *path, char *buf, size_t buflen);
int pfs_format_fullmeta(const char *path, char *buf, size_t buflen);

#ifdef __cplusplus
}
#endif

#endif
