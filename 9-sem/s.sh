# 1) kill any obviously stuck MacTeX / brew installers
pkill -f "brew install --cask mactex" 2>/dev/null || true
pkill -f "MacTeX" 2>/dev/null || true
pkill -f "Installer.app" 2>/dev/null || true

# 2) remove stale MacTeX downloads/locks
rm -f "/Users/user/Library/Caches/Homebrew/downloads/274b9b0186def695b370e3aa3db0dd42060742505c6433bcf1d8788ca8661ab8--mactex-20250308.pkg.incomplete"
rm -f ~/Library/Caches/Homebrew/downloads/*mactex*.incomplete 2>/dev/null || true
rm -f ~/Library/Caches/Homebrew/locks/* 2>/dev/null || true

# 3) retry install
brew install --cask mactex

