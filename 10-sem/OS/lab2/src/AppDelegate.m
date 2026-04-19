#import "AppDelegate.h"
#import "pfs_core.h"

#import <string.h>
#import <sys/stat.h>
#import <unistd.h>

@interface AppDelegate ()
@property (nonatomic, strong) NSWindow *window;
@property (nonatomic, strong) NSTableView *tableView;
@property (nonatomic, strong) NSTextView *detailTextView;
@property (nonatomic, strong) NSScrollView *detailScrollView;
@property (nonatomic, strong) NSImageView *imageView;
@property (nonatomic, strong) NSScrollView *tableScrollView;
@property (nonatomic, strong) NSButton *parentButton;
@end

@implementation AppDelegate {
    char _pathBuf[1024];
}

static NSColor *PFSPlatinumBackground(void) {
    return [NSColor colorWithCalibratedWhite:0.91 alpha:1.0];
}

static NSColor *PFSPlatinumPanel(void) {
    return [NSColor colorWithCalibratedWhite:0.93 alpha:1.0];
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

    NSSplitView *mainSplit = [[NSSplitView alloc] initWithFrame:NSMakeRect(0, 0, w, h)];
    mainSplit.vertical = YES;
    mainSplit.dividerStyle = NSSplitViewDividerStyleThin;
    mainSplit.wantsLayer = YES;
    mainSplit.layer.backgroundColor = PFSPlatinumBackground().CGColor;

    NSTableColumn *colName =
        [[NSTableColumn alloc] initWithIdentifier:@"name"];
    colName.title = @"Name";
    colName.width = 380;

    NSTableColumn *colKind =
        [[NSTableColumn alloc] initWithIdentifier:@"kind"];
    colKind.title = @"Kind";
    colKind.width = 72;

    self.tableView = [[NSTableView alloc] initWithFrame:NSZeroRect];
    [self.tableView addTableColumn:colName];
    [self.tableView addTableColumn:colKind];
    self.tableView.delegate = self;
    self.tableView.dataSource = self;
    self.tableView.target = self;
    self.tableView.doubleAction = @selector(onTableDoubleClick:);
    self.tableView.usesAlternatingRowBackgroundColors = YES;
    self.tableView.gridStyleMask = NSTableViewSolidHorizontalGridLineMask;

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
    self.detailTextView.font =
        [NSFont monospacedSystemFontOfSize:12 weight:NSFontWeightRegular];
    self.detailTextView.backgroundColor = PFSPlatinumPanel();
    self.detailTextView.drawsBackground = YES;
    self.detailTextView.string = @"";

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
    self.imageView.wantsLayer = YES;
    self.imageView.layer.backgroundColor = PFSPlatinumPanel().CGColor;

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

    [self reloadListingSelectingRow:0];
    [self.window makeKeyAndOrderFront:nil];
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
    path_join(tmp, sizeof(tmp), _pathBuf, (const char *)entry);
    memcpy(_pathBuf, tmp, sizeof(_pathBuf));
    [self reloadListingSelectingRow:0];
}

#pragma mark - Listing / detail

- (void)reloadListingSelectingRow:(NSInteger)selectRow {
    int n = fs_list_dir(_pathBuf);
    if (n < 0) {
        self.detailTextView.string = @"Could not read directory listing.";
        [self.tableView reloadData];
        return;
    }

    self.window.title = [NSString stringWithFormat:@"FS Viewer — %s", _pathBuf];
    [self.tableView reloadData];

    if (g_entry_count == 0) {
        [self.tableView deselectAll:nil];
        self.detailTextView.string = @"(empty directory)";
        self.imageView.image = nil;
        return;
    }

    if (selectRow < 0 || (uint64_t)selectRow >= g_entry_count) {
        selectRow = 0;
    }
    NSIndexSet *ix = [NSIndexSet indexSetWithIndex:(NSUInteger)selectRow];
    [self.tableView selectRowIndexes:ix byExtendingSelection:NO];
    [self updateDetailPanel];
}

- (void)updateDetailPanel {
    NSInteger row = self.tableView.selectedRow;
    if (row < 0 || (uint64_t)row >= g_entry_count) {
        self.detailTextView.string = @"";
        self.imageView.image = nil;
        return;
    }

    unsigned char *entry = g_entries + row * PFS_ENTRY_SIZE;
    const char *name = (const char *)entry;

    char full[1024];
    path_join(full, sizeof(full), _pathBuf, name);

    if (entry[PFS_ENTRY_OFF_ISDIR]) {
        int c = fs_count_jpg_png(full);
        self.detailTextView.string =
            [NSString stringWithFormat:@"Directory\nJPG/PNG files in this folder: %d\n", c];
        self.imageView.image = nil;
        return;
    }

    NSString *lower = [[NSString stringWithUTF8String:name] lowercaseString];
    if ([lower hasSuffix:@".png"]) {
        char detail[4096];
        if (png_format_ihdr_info(full, detail, sizeof(detail)) == 0) {
            self.detailTextView.string = [NSString stringWithUTF8String:detail];
        } else {
            self.detailTextView.string = @"Could not read PNG header.";
        }
        NSString *pathStr = [NSString stringWithUTF8String:full];
        self.imageView.image = [[NSImage alloc] initWithContentsOfFile:pathStr];
        return;
    }

    self.imageView.image = nil;

    struct stat st;
    if (lstat(full, &st) != 0) {
        self.detailTextView.string = @"lstat failed for the selected path.";
        return;
    }

    char tbuf[64];
    memset(tbuf, 0, sizeof(tbuf));

    if (st.st_birthtimespec.tv_sec != 0 || st.st_birthtimespec.tv_nsec != 0) {
        render_fmt_timespec_to_buf(st.st_birthtimespec.tv_sec,
                                   st.st_birthtimespec.tv_nsec, tbuf,
                                   sizeof(tbuf));
        self.detailTextView.string = [NSString
            stringWithFormat:@"File: %s\nCreation time: %s\n", name, tbuf];
    } else {
        render_fmt_timespec_to_buf(st.st_mtimespec.tv_sec,
                                   st.st_mtimespec.tv_nsec, tbuf,
                                   sizeof(tbuf));
        self.detailTextView.string =
            [NSString stringWithFormat:@"File: %s\nModified (no birth time): %s\n",
                                       name, tbuf];
    }
}

#pragma mark - NSTableViewDataSource

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView {
    return (NSInteger)g_entry_count;
}

- (id)tableView:(NSTableView *)tableView
    objectValueForTableColumn:(NSTableColumn *)tableColumn
                          row:(NSInteger)row {
    if (row < 0 || (uint64_t)row >= g_entry_count) {
        return @"";
    }

    unsigned char *entry = g_entries + row * PFS_ENTRY_SIZE;

    if ([tableColumn.identifier isEqualToString:@"name"]) {
        return [NSString stringWithUTF8String:(const char *)entry];
    }
    if ([tableColumn.identifier isEqualToString:@"kind"]) {
        return entry[PFS_ENTRY_OFF_ISDIR] ? @"folder" : @"file";
    }
    return @"";
}

#pragma mark - NSTableViewDelegate

- (void)tableViewSelectionDidChange:(NSNotification *)notification {
    [self updateDetailPanel];
}

@end
