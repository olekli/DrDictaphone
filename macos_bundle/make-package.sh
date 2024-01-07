#!/bin/sh

cd package/icon &&
sh make-icns.sh &&
cd ../.. &&

ln -fs package/DrDictaphone.spec . &&
pyinstaller --noconfirm DrDictaphone.spec
