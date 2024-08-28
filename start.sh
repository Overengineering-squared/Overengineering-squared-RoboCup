#!/bin/bash

current_datetime=$(date +'%Y-%m-%d_%H-%M-%S')
formatted_datetime=$(echo "$current_datetime" | sed 's/_/ /;s/-/ /;s/-/ /;s/_/ /')
output_file="$formatted_datetime.txt"

command="/usr/bin/python3 main.py"

mkdir -p "logs/"

cd "robot_v.3/Python/main/" || exit

$command > "../../../logs/$output_file" 2>&1

echo "Output saved to $output_file"
