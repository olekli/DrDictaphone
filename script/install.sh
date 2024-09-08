#!/bin/sh

TARGET="$1" &&
{ test -n "$TARGET" || TARGET="$HOME/DrDictaphone"; } &&
echo "Installing to $TARGET" &&
mkdir -p "$TARGET" &&
cd "$TARGET" &&
rm -fr .venv &&
python3 -m venv .venv &&
. .venv/bin/activate &&
pip install drdictaphone &&
python -m drdictaphone.cli install "$TARGET"
