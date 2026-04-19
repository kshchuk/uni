#import "AppDelegate.h"
#import "pfs_core.h"

#import <string.h>
#import <unistd.h>

@interface AppDelegate ()
@property (nonatomic, strong) NSWindow *window;
@property (nonatomic, strong) NSTableView *tableView;
@property (nonatomic, strong) NSTextView *detailTextView;
@property (nonatomic, strong) NSScrollView *detailScrollView;
@property (nonatomic, strong) NSImageView *imageView;
@property (nonatomic, strong) NSScrollView *tableScrollView;
@property (nonatomic, strong) NSButton *parentButton;
- (void)pfs_reloadInitialListing:(id)unused;
- (void)pfs_setPathAndReload:(NSString *)path;
- (void)pfs_setDetailPlainText:(NSString *)text;
@end

@implementation AppDelegate {
    char _pathBuf[1024];
    BOOL _suppressSelectionUpdates;
}

static NSColor *PFSPlatinumBackground(void) {
    return [NSColor colorWithCalibratedWhite:0.91 alpha:1.0];
}

static NSColor *PFSPlatinumPanel(void) {
    return [NSColor colorWithCalibratedWhite:0.93 alpha:1.0];
}

static NSString *PFSCBoundedUTF8(const char *buf, size_t bufsize) {
    char tmp[1024];
    size_t cap = sizeof(tmp) - 1;
    size_t n = bufsize - 1 < cap ? bufsize - 1 : cap;
    memcpy(tmp, buf, n);
    tmp[n] = '\0';
    NSString *s = [NSString stringWithUTF8String:tmp];
    return s ?: @"";
}

static void PFSCopyEntryName(char out[PFS_ENTRY_NAME_LEN],
                             const unsigned char *entryRow) {
    memcpy(out, entryRow, PFS_ENTRY_NAME_LEN - 1);
    out[PFS_ENTRY_NAME_LEN - 1] = '\0';
}

static NSString *PFSFormatFileMetadata(const char *fullPath) {
    long long sz = pfs_file_size(fullPath);
    if (sz < 0) {
        return @"";
    }

    NSString *sizeStr;
    if (sz < 1024) {
        sizeStr = [NSString stringWithFormat:@"%lld B", sz];
    } else if (sz < 1024LL * 1024) {
        sizeStr = [NSString stringWithFormat:@"%.1f KiB (%lld B)",
                                             sz / 1024.0, sz];
    } else {
        sizeStr = [NSString stringWithFormat:@"%.1f MiB (%lld B)",
                                             sz / (1024.0 * 1024.0), sz];
    }

    char metaBuf[1024] = {0};
    NSString *rest = @"";
    if (pfs_format_fullmeta(fullPath, metaBuf, sizeof(metaBuf)) == 0) {
        rest = [NSString stringWithUTF8String:metaBuf] ?: @"";
    }

    if (rest.length == 0) {
        return [NSString stringWithFormat:@"Size: %@\n", sizeStr];
    }
    return [NSString stringWithFormat:@"Size: %@\n%@\n", sizeStr, rest];
}

- (void)pfs_setDetailPlainText:(NSString *)text {
    NSTextView *tv = self.detailTextView;
    if (!tv) {
        return;
    }
    NSString *s = text ?: @"";
    if (s.length == 0 && tv.string.length == 0) {
        return;
    }
    tv.string = s;
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    if (!getcwd(_pathBuf, sizeof(_pathBuf))) {
        strcpy(_pathBuf, "/");
    }

    CGFloat w = 920;
    CGFloat h = 560;
    NSRect rect = NSMakeRect(120, 120, w, h);

    NSUInteger style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                       NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable;

    self.window = [[NSWindow alloc] initWithContentRect:rect
                                              styleMask:style
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    self.window.title = @"FS Viewer — OS Lab 2 / variant 4";
    self.window.minSize = NSMakeSize(640, 400);
    self.window.backgroundColor = PFSPlatinumBackground();

    NSAppearance *lightAqua = [NSAppearance appearanceNamed:NSAppearanceNameAqua];

    NSSplitView *mainSplit = [[NSSplitView alloc] initWithFrame:NSMakeRect(0, 0, w, h)];
    mainSplit.vertical = YES;
    mainSplit.dividerStyle = NSSplitViewDividerStyleThin;

    NSTableColumn *colName =
        [[NSTableColumn alloc] initWithIdentifier:@"name"];
    colName.title = @"Name";
    colName.width = 380;

    NSTableColumn *colKind =
        [[NSTableColumn alloc] initWithIdentifier:@"kind"];
    colKind.title = @"Kind";
    colKind.width = 72;

    self.tableView =
        [[NSTableView alloc] initWithFrame:NSMakeRect(0, 0, 420, h - 56)];
    [self.tableView addTableColumn:colName];
    [self.tableView addTableColumn:colKind];
    self.tableView.delegate = self;
    self.tableView.dataSource = self;
    self.tableView.target = self;
    self.tableView.doubleAction = @selector(onTableDoubleClick:);
    self.tableView.usesAlternatingRowBackgroundColors = YES;

    self.tableScrollView =
        [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 440, h)];
    self.tableScrollView.documentView = self.tableView;
    self.tableScrollView.hasVerticalScroller = YES;
    self.tableScrollView.borderType = NSBezelBorder;
    self.tableScrollView.drawsBackground = YES;
    self.tableScrollView.backgroundColor = PFSPlatinumPanel();

    NSSplitView *rightSplit = [[NSSplitView alloc] initWithFrame:NSMakeRect(0, 0, w - 460, h)];
    rightSplit.vertical = NO;
    rightSplit.dividerStyle = NSSplitViewDividerStyleThin;

    NSSize sz = NSMakeSize(w - 460, h);
    NSRect textFrame = NSMakeRect(0, 0, sz.width, sz.height * 0.45);

    self.detailTextView =
        [[NSTextView alloc] initWithFrame:textFrame];
    self.detailTextView.editable = NO;
    self.detailTextView.selectable = YES;
    self.detailTextView.font = [NSFont userFixedPitchFontOfSize:12];
    self.detailTextView.backgroundColor = PFSPlatinumPanel();
    self.detailTextView.drawsBackground = YES;
    self.detailTextView.textColor = [NSColor textColor];
    [self pfs_setDetailPlainText:@""];

    self.detailScrollView =
        [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, sz.width, sz.height * 0.45)];
    self.detailScrollView.documentView = self.detailTextView;
    self.detailScrollView.hasVerticalScroller = YES;
    self.detailScrollView.borderType = NSBezelBorder;
    self.detailScrollView.drawsBackground = YES;
    self.detailScrollView.backgroundColor = PFSPlatinumPanel();

    self.imageView =
        [[NSImageView alloc] initWithFrame:NSMakeRect(0, 0, sz.width, sz.height * 0.55)];
    self.imageView.imageScaling = NSImageScaleProportionallyDown;
    self.imageView.imageAlignment = NSImageAlignCenter;
    self.imageView.editable = NO;

    [rightSplit addSubview:self.detailScrollView];
    [rightSplit addSubview:self.imageView];

    NSView *leftContainer = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 460, h)];
    leftContainer.autoresizesSubviews = YES;

    self.parentButton =
        [[NSButton alloc] initWithFrame:NSMakeRect(12, h - 36, 140, 28)];
    self.parentButton.title = @"Parent folder";
    self.parentButton.bezelStyle = NSBezelStyleTexturedRounded;
    self.parentButton.target = self;
    self.parentButton.action = @selector(goParent:);
    self.parentButton.autoresizingMask = NSViewMinYMargin | NSViewMaxXMargin;

    self.tableScrollView.frame = NSMakeRect(8, 8, 444, h - 48);
    self.tableScrollView.autoresizingMask =
        NSViewWidthSizable | NSViewHeightSizable;

    [leftContainer addSubview:self.tableScrollView];
    [leftContainer addSubview:self.parentButton];

    [mainSplit addSubview:leftContainer];
    [mainSplit addSubview:rightSplit];

    mainSplit.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;

    self.window.contentView = mainSplit;
    self.window.appearance = lightAqua;
    self.window.contentView.appearance = lightAqua;

    [self.window makeKeyAndOrderFront:nil];
    [self performSelector:@selector(pfs_reloadInitialListing:)
               withObject:nil
               afterDelay:0.05];
}

- (void)pfs_reloadInitialListing:(id)unused {
    [self reloadListingSelectingRow:0];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}

#pragma mark - Actions

- (void)goParent:(id)sender {
    path_parent_inplace(_pathBuf);
    [self reloadListingSelectingRow:0];
}

- (void)onTableDoubleClick:(id)sender {
    NSInteger row = self.tableView.clickedRow;
    if (row < 0 || (uint64_t)row >= g_entry_count) {
        return;
    }
    unsigned char *entry = g_entries + row * PFS_ENTRY_SIZE;
    if (!entry[PFS_ENTRY_OFF_ISDIR]) {
        return;
    }

    char tmp[1024];
    char nameBuf[PFS_ENTRY_NAME_LEN];
    PFSCopyEntryName(nameBuf, entry);
    path_join(tmp, sizeof(tmp), _pathBuf, nameBuf);

    NSString *pathStr = [NSString stringWithUTF8String:tmp];
    if (!pathStr.length) {
        pathStr = PFSCBoundedUTF8(tmp, sizeof(tmp));
    }

    [self performSelector:@selector(pfs_setPathAndReload:)
               withObject:pathStr
               afterDelay:0];
}

- (void)pfs_setPathAndReload:(NSString *)path {
    const char *u = path.UTF8String;
    if (!u) {
        return;
    }
    strlcpy(_pathBuf, u, sizeof(_pathBuf));
    [self reloadListingSelectingRow:0];
}

#pragma mark - Listing / detail

- (void)reloadListingSelectingRow:(NSInteger)selectRow {
    int n = fs_list_dir(_pathBuf);
    if (n < 0) {
        [self pfs_setDetailPlainText:@"Could not read directory listing."];
        _suppressSelectionUpdates = YES;
        [self.tableView reloadData];
        _suppressSelectionUpdates = NO;
        return;
    }

    self.window.title =
        [NSString stringWithFormat:@"FS Viewer — %@",
                                   PFSCBoundedUTF8(_pathBuf, sizeof(_pathBuf))];
    _suppressSelectionUpdates = YES;
    [self.tableView reloadData];
    _suppressSelectionUpdates = NO;

    if (g_entry_count == 0) {
        [self.tableView deselectAll:nil];
        [self pfs_setDetailPlainText:@"(empty directory)"];
        self.imageView.image = nil;
        return;
    }

    if (selectRow < 0 || (uint64_t)selectRow >= g_entry_count) {
        selectRow = 0;
    }
    NSIndexSet *ix = [NSIndexSet indexSetWithIndex:(NSUInteger)selectRow];
    _suppressSelectionUpdates = YES;
    [self.tableView selectRowIndexes:ix byExtendingSelection:NO];
    _suppressSelectionUpdates = NO;

    [self updateDetailPanel];
}

- (void)updateDetailPanel {
    NSInteger row = self.tableView.selectedRow;
    if (row < 0 || (uint64_t)row >= g_entry_count) {
        [self pfs_setDetailPlainText:@""];
        self.imageView.image = nil;
        return;
    }

    unsigned char *entry = g_entries + row * PFS_ENTRY_SIZE;
    char nameBuf[PFS_ENTRY_NAME_LEN];
    PFSCopyEntryName(nameBuf, entry);

    char full[1024];
    path_join(full, sizeof(full), _pathBuf, nameBuf);

    if (entry[PFS_ENTRY_OFF_ISDIR]) {
        int c = fs_count_jpg_png(full);
        NSString *body =
            [NSString stringWithFormat:@"Directory\nJPG/PNG files in this folder: %d\n",
                                       c];
        [self pfs_setDetailPlainText:body];
        self.imageView.image = nil;
        return;
    }

    NSString *meta = PFSFormatFileMetadata(full);
    NSString *lower = [[NSString stringWithUTF8String:nameBuf] lowercaseString];

    if ([lower hasSuffix:@".png"]) {
        char detail[4096];
        NSString *pngText;
        if (png_format_ihdr_info(full, detail, sizeof(detail)) == 0) {
            pngText = [NSString stringWithUTF8String:detail]
                          ?: @"[invalid UTF-8 in PNG info]";
        } else {
            pngText = @"Could not read PNG header.";
        }
        [self pfs_setDetailPlainText:
                  [NSString stringWithFormat:@"%@\n%@", meta, pngText]];
        NSString *pathStr = [NSString stringWithUTF8String:full];
        if (pathStr.length > 0) {
            self.imageView.image = [[NSImage alloc] initWithContentsOfFile:pathStr];
        } else {
            self.imageView.image = nil;
        }
        return;
    }

    if ([lower hasSuffix:@".jpg"] || [lower hasSuffix:@".jpeg"]) {
        [self pfs_setDetailPlainText:
                  [NSString stringWithFormat:@"JPEG image\n%@", meta]];
        NSString *pathStr = [NSString stringWithUTF8String:full];
        self.imageView.image =
            pathStr.length ? [[NSImage alloc] initWithContentsOfFile:pathStr] : nil;
        return;
    }

    self.imageView.image = nil;
    [self pfs_setDetailPlainText:meta];
}

#pragma mark - NSTableViewDataSource

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView {
    return (NSInteger)g_entry_count;
}

- (id)tableView:(NSTableView *)tableView
    objectValueForTableColumn:(NSTableColumn *)tableColumn
                          row:(NSInteger)row {
    if (!tableColumn || row < 0 || (uint64_t)row >= g_entry_count) {
        return @"";
    }

    unsigned char *entry = g_entries + row * PFS_ENTRY_SIZE;
    NSString *colId = tableColumn.identifier;

    if ([colId isEqualToString:@"name"]) {
        NSString *s = [NSString stringWithUTF8String:(const char *)entry];
        return s ?: @"";
    }
    if ([colId isEqualToString:@"kind"]) {
        return entry[PFS_ENTRY_OFF_ISDIR] ? @"folder" : @"file";
    }
    return @"";
}

#pragma mark - NSTableViewDelegate

- (void)tableViewSelectionDidChange:(NSNotification *)notification {
    if (_suppressSelectionUpdates) {
        return;
    }
    [self updateDetailPanel];
}

@end
