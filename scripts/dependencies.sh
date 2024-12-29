#!/usr/bin/env bash

python_exec=$(which python3 2>/dev/null || which python 2>/dev/null)

if [[ "$USER" == root ]]; then
    echo "Please run the install script as non-root user."
    exit 1
fi

# Check for pyusb installation
"${python_exec}" -c 'import usb.core' 2>/dev/null
if [ $? = 1 ]; then
    echo "Install (locally or system-wide) the pyusb Python module first."
    read -rp "Do you want to install it locally? [y/N] " response

    if [[ "${response}" == [yY] ]]; then
        "${python_exec}" -m pip install --user pyusb
    else
        echo "To install locally, run: ${python_exec} -m pip install --user pyusb"
        exit 2
    fi
fi

# Check for PyQT6 installation
"${python_exec}" -c 'import PyQt6' 2>/dev/null
if [ $? = 1 ]; then
    echo "Install (locally or system-wide) the PyQt6 Python module first."
    echo "Due to its size it is recommended to install via the distro's package manager."
    echo
    read -rp "Do you want to install it locally? [y/N] " response

    if [[ "${response}" == [yY] ]]; then
        "${python_exec}" -m pip install --user PyQt6
    else
        echo "To install locally, run: ${python_exec} -m pip install --user PyQt6"
        echo "To install at system level, try running the following command. Note that the package name might differ depending on your distro:"
        
        which dnf 1>/dev/null 2>&1
        dnf=$?
        which yum 1>/dev/null 2>&1
        yum=$?
        which apt 1>/dev/null 2>&1
        apt=$?
        which apt-get 1>/dev/null 2>&1
        apt_get=$?
        which pacman 1>/dev/null 2>&1
        pacman=$?
        which zypper 1>/dev/null 2>&1
        zypper=$?


        if [ ${dnf} == 0 ]; then
            echo "sudo dnf install python3-pyqt6"
        elif [ ${yum} == 0 ]; then
            echo "sudo yum install python3-pyqt6"
        elif [ ${apt} == 0 ]; then
            echo "sudo apt install python3-pyqt6"
        elif [ ${apt_get} == 0 ]; then
            echo "sudo apt-get install python3-pyqt6"
        elif [ ${pacman} == 0 ]; then
            echo "sudo pacman -S python3-pyqt6"
        elif [ ${zypper} == 0 ]; then
            echo "sudo zypper -S python3-PyQt6"
        else
            echo "** Unknown package manager, please install manually **"
        fi

        exit 3
    fi
fi

# Check for qasync installation
"${python_exec}" -c 'import qasync' 2>/dev/null
if [ $? = 1 ]; then
    echo "Install (locally or system-wide) the qasync Python module first."
    read -rp "Do you want to install it locally? [y/N] " response

    if [[ "${response}" == [yY] ]]; then
        "${python_exec}" -m pip install --user qasync
    else
        echo "To install locally, run: ${python_exec} -m pip install --user qasync"
        exit 2
    fi
fi
