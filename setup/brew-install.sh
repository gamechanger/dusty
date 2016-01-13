#!/bin/bash

set -e

cp $1/com.gamechanger.dusty.plist /Library/LaunchDaemons/com.gamechanger.dusty.plist
launchctl unload /Library/LaunchDaemons/com.gamechanger.dusty.plist || true
chmod +x $1/dusty
$1/dusty -d --preflight-only
launchctl load /Library/LaunchDaemons/com.gamechanger.dusty.plist
