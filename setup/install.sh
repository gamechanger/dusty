release=0.0.1
function bold_echo {
    echo -e "\033[1m$1\033[0m"
}
bold_echo "Downloading dusty files"
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dustyd > /usr/local/bin/dustyd
bold_echo "Authenticating as super user... needed to setup daemon"
sudo -v
sudo curl -L -o /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist https://raw.githubusercontent.com/gamechanger/dusty/master/setup/org.gamechanger.dustyd.plist
bold_echo "Adding & resetting dustyd daemon"
sudo launchctl unload /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
sudo launchctl load /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
