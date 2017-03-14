#!/usr/bin/env bash

pyinstaller --onefile app.spec
cp dist/app app-skeleton/safetybar.app/Contents/MacOS/safetybar