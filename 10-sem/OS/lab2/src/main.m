#import <Cocoa/Cocoa.h>
#import "AppDelegate.h"

/* NSApplication.delegate is assign; retain the delegate for process lifetime. */
static AppDelegate *PFSHeldAppDelegate = nil;

int main(int argc, const char *argv[]) {
    (void)argc;
    (void)argv;

    @autoreleasepool {
        [NSApplication sharedApplication];
        PFSHeldAppDelegate = [[AppDelegate alloc] init];
        NSApp.delegate = PFSHeldAppDelegate;
        NSApp.activationPolicy = NSApplicationActivationPolicyRegular;
        [NSApp activateIgnoringOtherApps:YES];
    }

    [NSApp run];
    return 0;
}
