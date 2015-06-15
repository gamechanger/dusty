set -e

# This is set by Jenkins during release
release=

function bold_echo {
    echo -e "\033[1m$1\033[0m"
}

bold_echo "Downloading dusty binary"
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
chmod +x /usr/local/bin/dusty
bold_echo "Authenticating as super user... needed to setup daemon"
sudo -v
bold_echo "Resetting dusty daemon"
sudo curl -L -o /System/Library/LaunchDaemons/org.gamechanger.dusty.plist https://raw.githubusercontent.com/gamechanger/dusty/$release/setup/org.gamechanger.dusty.plist
sudo launchctl unload /System/Library/LaunchDaemons/org.gamechanger.dusty.plist
bold_echo "Testing dusty daemon's preflight..."
sudo dusty -d --preflight-only || (bold_echo "Preflight failed; not loading daemon"; exit 1)
bold_echo "Loading dusty daemon"
sudo launchctl load /System/Library/LaunchDaemons/org.gamechanger.dusty.plist
