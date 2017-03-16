#!/usr/bin/env bash

GITHUB_USER="jayfk"
GITHUB_REPO="menubar"


if [[ $# -eq 0 ]] ; then
    echo 'usage: release version'
    exit 1
fi

version=$1

echo $version

sed -i '' "s/__version__ = '[^0-9.]*\([0-9.]*\).*'/__version__ = '${version}'/" app.py

pyinstaller --onefile app.spec
cp dist/app app-skeleton/safetybar.app/Contents/MacOS/safetybar
rm dist/safetybar.dmg
appdmg app-skeleton/appdmg.json dist/safetybar.dmg

git commit -a -m "new release ${version}"
git tag $version
git push origin master --tags

github-release release --user $GITHUB_USER --repo $GITHUB_REPO --tag $version --name $version
github-release upload --user $GITHUB_USER --repo $GITHUB_REPO --tag $version --name 'safetybar.dmg' --file dist/safetybar.dmg
