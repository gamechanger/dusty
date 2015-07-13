set -e

# This is set by Jenkins during release
release=
LEGACY_INSTALL_ROOT=/System/Library/LaunchDaemons
LEGACY_PLIST_NAME=org.gamechanger.dusty.plist
INSTALL_ROOT=/Library/LaunchDaemons
PLIST_NAME=com.gamechanger.dusty.plist

function bold_echo {
    echo -e "\033[1m$1\033[0m"
}

bold_echo "Downloading dusty binary"
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
chmod +x /usr/local/bin/dusty
bold_echo "Authenticating as super user... needed to setup daemon"
sudo -v
bold_echo "Resetting dusty daemon"
sudo curl -L -o $INSTALL_ROOT/$PLIST_NAME https://raw.githubusercontent.com/gamechanger/dusty/$release/setup/$PLIST_NAME
sudo launchctl unload $INSTALL_ROOT/$PLIST_NAME
bold_echo "Testing dusty daemon's preflight..."
sudo -H dusty -d --preflight-only || (bold_echo "Preflight failed; not loading daemon"; exit 1)
bold_echo "Loading dusty daemon"
sudo launchctl load $INSTALL_ROOT/$PLIST_NAME

# Clean up install from legacy install directory if it exists
if [ -f $LEGACY_INSTALL_ROOT/$LEGACY_PLIST_NAME ]; then
    echo "Removing legacy install plist in $LEGACY_INSTALL_ROOT"
    sudo launchctl unload $LEGACY_INSTALL_ROOT/$LEGACY_PLIST_NAME
    sudo rm $LEGACY_INSTALL_ROOT/$LEGACY_PLIST_NAME
fi
