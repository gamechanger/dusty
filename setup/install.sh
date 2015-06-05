release=0.0.1
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dusty > /usr/local/bin/dusty
curl -L https://github.com/gamechanger/dusty/releases/download/$release/dustyd > /usr/local/bin/dustyd
sudo curl -L -o /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist https://raw.githubusercontent.com/gamechanger/dusty/master/setup/org.gamechanger.dustyd.plist
sudo launchctl unload /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
sudo launchctl load /System/Library/LaunchDaemons/org.gamechanger.dustyd.plist
