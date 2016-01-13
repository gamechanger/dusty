#!/bin/bash

set -e

cp com.gamechanger.dusty.plist /Library/LaunchDaemons/com.gamechanger.dusty.plist
launchctl unload /Library/LaunchDaemons/com.gamechanger.dusty.plist || true
dusty -d --preflight-only
launchctl load /Library/LaunchDaemons/com.gamechanger.dusty.plist
