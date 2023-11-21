#!/bin/sh

clear &&
cat "$1" &&
fswatch --event=Updated -0 "$1" | xargs -0 -n1 -I{} sh -c "clear; cat $1"
