#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

desktop_file_contents="[Desktop Entry]\nName=Robot\nType=Application\nExec=bash -c 'cd $script_dir && ./start.sh'"

autostart_dir="/home/pi/.config/autostart"

desktop_file_path="$autostart_dir/robot.desktop"

mkdir -p "$autostart_dir"

echo -e "$desktop_file_contents" > "$desktop_file_path"

chmod +x "$desktop_file_path"

mv "$desktop_file_path" "$autostart_dir/"

echo "robot.desktop file has been created and moved to $autostart_dir."