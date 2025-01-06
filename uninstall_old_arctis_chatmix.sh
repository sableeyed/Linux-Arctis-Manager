#!/usr/bin/env bash

## This script uninstalls the previous "arctis-chatmix" software,
## due to the name change.

bin_local_dir="$HOME/.local/bin/"
systemd_local_dir="$HOME/.config/systemd/user/"
udev_rules_dir="/etc/udev/rules.d/"

local_bin_files_and_folders=("arctis_chatmix.py" "arctis_chatmix")
local_systemd_file="arctis-pcm.service"
udev_rules_file="91-steelseries-arctis.rules"

function rem {
    file="${*: -1:1}"
    dry_run=""
    sudo_run=""

    if [[ "${*}" =~ "--dry-run" ]]; then
        dry_run="echo "
    fi

    if [[ "${*}" =~ "--sudo" ]]; then
        sudo_run=" sudo "
    fi
    
    if [ -d "$file" ]; then
        cmd="rm -r $file"
    elif [ -f "$file" ]; then
        cmd="rm $file"
    else
        cmd=""
    fi

    if [ "${cmd}" == "" ]; then
        return
    fi

    cmd="${dry_run} ${sudo_run} ${cmd}"

    eval "${cmd}"
}

systemctl --user disable --now arctis-pcm.service 2>/dev/null

for file in "${local_bin_files_and_folders[@]}"; do
    rem "${bin_local_dir}${file}"
done

rem --sudo "${systemd_local_dir}${local_systemd_file}"
rem --sudo "${udev_rules_dir}${udev_rules_file}"
