release=0.0.1
echo -e "\033[1mDownloading dusty files\033[0m"
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dustyd > /usr/local/bin/dustyd
echo -e "\033[1mAuthenticating as super user... needed to setup daemon\033[0m"
sudo -v
sudo curl -L -o /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist https://raw.githubusercontent.com/gamechanger/dusty/master/setup/org.gamechanger.dustyd.plist
echo -e "\033[1mAdding & resetting dustyd daemon\033[0m"
sudo launchctl unload /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
sudo launchctl load /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
