#!/usr/bin/env bash

set -e

brew cask zap dusty 2> /dev/null

LEGACY_DAEMON=/System/Library/LaunchDaemons/org.gamechanger.dusty.plist
DAEMON=/Library/LaunchDaemons/com.gamechanger.dusty.plist

sudo launchctl unload "$LEGACY_DAEMON"
sudo rm "$LEGACY_DAEMON" 2> /dev/null

sudo launchctl unload "$DAEMON"
sudo rm "$DAEMON" 2> /dev/null

sudo rm /usr/local/bin/dusty

echo "Dusty has been uninstalled!"

