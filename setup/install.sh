set -e

# This is set by Jenkins during release
release=

function bold_echo {
    echo -e "\033[1m$1\033[0m"
}

bold_echo "Downloading dusty files"
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
chmod +x /usr/local/bin/dusty
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dustyd > /usr/local/bin/dustyd
chmod +x /usr/local/bin/dustyd
bold_echo "Authenticating as super user... needed to setup daemon"
sudo -v
bold_echo "Resetting dustyd daemon"
sudo curl -L -o /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist https://raw.githubusercontent.com/gamechanger/dusty/$release/setup/org.gamechanger.dustyd.plist
sudo launchctl unload /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
bold_echo "Testing dustyd's preflight..."
sudo dustyd --preflight-only || (bold_echo "Preflight failed; not loading daemon"; exit 1)
bold_echo "Loading dustyd daemon"
sudo launchctl load /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
