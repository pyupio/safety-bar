#!/usr/bin/env bash

pyinstaller --onefile app.spec
cp dist/app app-skeleton/safetybar.app/Contents/MacOS/safetybar
rm dist/safetybar.dmg
appdmg app-skeleton/appdmg.json dist/safetybar.dmg