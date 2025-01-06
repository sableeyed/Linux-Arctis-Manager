#!/usr/bin/env bash

if [ -z "${PREFIX}" ]; then
    install_prefix=/usr/local
else
    install_prefix=${PREFIX}
fi

# Files to install
lib_files_and_dirs=("arctis_manager.py" "arctis_manager")
bin_files=("bin/arctis-manager")
systemd_service_file="systemd/arctis-manager.service"
udev_rules_file="udev/91-steelseries-arctis.rules"

# Install directories
bin_dir="${install_prefix}/bin"
lib_dir="${install_prefix}/lib/arctis-manager"
udev_dir="/usr/lib/udev/rules.d/"
systemd_dir="/usr/lib/systemd/user/"

function install() {
    echo "Installing Arctis Manager..."

    sudo mkdir -p "${bin_dir}"
    sudo mkdir -p "${lib_dir}"

    echo "Installing binaries in ${bin_dir}"
    for file in "${bin_files[@]}"; do
        dest_file="${bin_dir}/$(basename "${file}")"
        sudo cp "${file}" "${dest_file}"

        # Replace placeholders
        sudo sed -i "s|{{LIBDIR}}|${lib_dir}|g" "${dest_file}"
    done

    echo "Installing application data in ${lib_dir}"
    for file in "${lib_files_and_dirs[@]}"; do
        if [ -f "${file}" ]; then
            sudo cp "${file}" "${lib_dir}/"
        elif [ -d "${file}" ]; then
            sudo cp -r "${file}" "${lib_dir}/"
        fi
    done

    # Note: using sudo with pip to install modules
    # It is harmless, as it will target a custom folder
    echo "Installing python dependencies in ${lib_dir}"
    sudo python3 -m pip install --upgrade --quiet --root-user-action=ignore -r requirements.txt --target "${lib_dir}"

    # Udev rules
    echo "Installing udev rules."
    sudo cp "${udev_rules_file}" "${udev_dir}"
    sudo udevadm control --reload
    sudo udevadm trigger

    # SystemD service
    echo "Installing and enabling systemd user service."
    systemctl --user disable --now "$(basename ${systemd_service_file})" 2>/dev/null
    sudo cp "${systemd_service_file}" "${systemd_dir}"
    systemctl --user enable --now "$(basename ${systemd_service_file})"
}

function uninstall() {
    echo "Uninstalling Arctis Manager..."
    echo

    echo "Removing udev rules."
    sudo rm -rf "${udev_dir}/$(basename ${udev_rules_file})" 2>/dev/null

    echo "Removing user systemd service."
    # systemd service
    systemctl --user disable --now "$(basename ${systemd_service_file})" 2>/dev/null
    sudo rm -rf "${systemd_dir}/$(basename ${systemd_service_file})" 2>/dev/null

    # Remove the custom lib dir
    echo "Removing application data."
    sudo rm -rf "${lib_dir}" 2>/dev/null
    for file in "${bin_files[@]}"; do
        sudo rm -rf "${bin_dir}/$(basename "${file}")" 2>/dev/null
    done
}

# Uninstall previous version
./uninstall_old_arctis_chatmix.sh

if [[ -v UNINSTALL ]]; then
    uninstall
else
    install
fi
