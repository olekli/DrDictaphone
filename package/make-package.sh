#!/bin/sh

cd package/icon &&
sh make-icns.sh &&
cd ../.. &&

ln -fs package/drdictaphone-internal.spec . &&
ln -fs package/DrDictaphone.spec . &&
pyinstaller --noconfirm drdictaphone-internal.spec &&
pyinstaller --noconfirm DrDictaphone.spec
