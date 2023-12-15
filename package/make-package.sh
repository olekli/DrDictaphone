#!/bin/sh

cd package/icon &&
sh make-icns.sh &&
cd ../.. &&

ln -fs package/drdictaphone.spec . &&
pyinstaller --noconfirm drdictaphone.spec
