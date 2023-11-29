#!/bin/sh

cd package/icon &&
sh make-icns.sh &&
cd ../..

pyinstaller \
  --name drdictaphone-internal \
  --add-data=post_processor:post_processor \
  --add-data=instructions:instructions \
  --add-data=tools:tools \
  --add-data=gpt_model:gpt_model \
  --add-data=profile:profile \
  --noconfirm \
  main.py &&

pyinstaller \
  --name DrDictaphone \
  --windowed \
  --add-data=dist/drdictaphone-internal:app \
  --icon package/icon/icon.icns \
  --noconfirm \
  package/launch.py
