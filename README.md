# Linux-Arctis-Manager

## Important Licensing Notice

`Linux-Arctis-Manager` is under the GPLv3 license. While the GPL license does permit commercial use, it is **strongly discouraged** to reuse the work herein for any for-profit purpose as it relates to the usage of a third party proprietary hardware device.


## Overview

The SteelSeries Arctis headsets series include a variety of features, like two mixable channels for VoIP and gaming (known as "ChatMix"), a hardware modulation knob, side-tone management, gain, etc. This is done partly hardware and partly software side, though the SteelSeries Engine (now included in the GG software) is required to setup and manage them all. If no software is used, only the very basic features are enabled (stereo audio out, mic in, hardware mute, possibly ANC).

This project aims to fill the gap, allowing the user to easily manage his/her own device on Linux distributions. On the plus side, this software is way lighter than SteelSeries's original :D

## Install

### Requirements

The software is based on the following prerequisites:

- PulseAudio (very common in modern Linux distributions), including the `pactl` command line (perhaps not installed by default, possibly the `pulseaudio-utils` system package)
- Python 3.9+ with `pip` installed
- Python modules (they will be installed automatically in the install directory via pip)
  - [dbus-next](https://github.com/altdesktop/python-dbus-next) - DBus library
  - [PyUSB](https://pyusb.github.io/pyusb/) - USB communication library
  - [qasync](https://github.com/CabbageDevelopment/qasync) - seamless async integration with Qt applications
  - [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) (suggested: globally due to its size) - Qt6 bindings for UI parts

### Execution

In order to install the application, simply run `./install.sh` (as user, not as root). In order to uninstall, prepend `UNINSTALL= `, i.e. `UNINSTALL= ./install.sh`.

An optional `PREFIX` variable can be defined to install the software in a custom location (default: `/usr/local`)

#### Installed files

The following parts will be installed:
- `/usr/lib/udev/rules.d/`: udev rules to set the ownership of the `/dev` device and to create a `/dev/steelseries/arctis` symlink to trigger the service (see below). The ownership part is not perfect for multi-users setups, but I'm working on it.
- `/usr/lib/systemd/user/`: user space's systemd service, which starts up at device plugin (or user's login) and shuts down at device plug-out (or user's log off).
- `/usr/local/lib/arctis-manager` (or `$PREFIX/lib/arctis-manager`): the Python application, including the service which communicates to the device, and a system tray icon which will display all the available information. If any setting is configurable software-side, the system tray app will show the relative action to open the settings menu.
- `/usr/local/bin/arctis-manager` (or `$PREFIX/bin/arctis-manager`): a bash script to start the service.
- `/usr/share/icons/hicolor/scalable/apps/arctis_manager.svg`: the desktop application's icon.
- `/usr/local/share/applications/ArctisManager.desktop` (or `$PREFIX/share/applications/ArctisManager.desktop`): the desktop application's definition file.

## Screenshots

### System tray application
![System tray application](docs/img/system_tray_app.png)

### Settings window (in the example: Arctis Nova Pro Wireless)
![Settings window](docs/img/settings_window.png)


**Note**: your device should automatically be configured after installation. If not, please unplug and plug the device again.

## Supported devices

- **Arctis 7+** (original development by [birdls](https://github.com/birdybirdonline))
  - Variants: PS5, XBOX, Destiny (only name and device id are changed)
- **Arctis Nova Pro Wireless** (developed by [Giacomo Furlan](https://github.com/elegos)). Note: the PulseAudio's channel's volume will stay at 100% even turning the knob, because it is managed by the GameDAC gen2 directly, so applying an audio reduction would apply it twice.
  - Variants: X (name and device id changed)

## How to add the support to a new device

The software has been rewritten from scratch from the original project to have an underlaying framework, in order to allow developers easily add new devices to the support list.

In order to support a new device you need to:

- add a new set of rules in [system-config/91-steelseries-arctis.rules](system-config/91-steelseries-arctis.rules) -> if having troubles with udev selector with composite USB devices, you might start from `udevadm info --attribute-walk --name=/dev/input/by-id/usb-SteelSeries_Arctis_[your specific device here]`. Take a look at the Nova Pro Wireless's rules to get an idea.
- Add a new [DeviceManager](arctis_chatmix/device_manager/device_manager.py) and its relative [DeviceStatus](arctis_chatmix/device_manager/device_status.py) in [arctis_chatmix/devices/](arctis_chatmix/devices/). Read the [Arctis Nova Pro Wireless](arctis_chatmix/devices/device_arctis_nova_pro_wireless.py) definition to get the idea.
- Update the [lang/](lang/) json files, if you introduced new `DeviceStatus` attributes and/or values. By default untranslatable items will go untranslated.

The new device will automatically be registered for you in the application.

If your work does the job, consider forking the repository and open a pull request.

Important notes:

- when working on the repository and running the application for debugging, remember to stop the service via `systemctl --user disable --now arctis-pcm.service`. Once finished, you can enable it again via `sysetmctl --user enable arctis-pcm.service`.
- if working with vscode, a launch setup is ready to use (`arctis_chatmix debug`) which will run the software with debug logging
- remember to refresh your installation once finished (see installation section)


### Need help on reverse engineering?

First try the [(Windows) USB analyzer guide](docs/USB_ANALYZER.md)!

Then try looking at the [wireshark guide](docs/WIRESHARK.md)!

### Do I need to override the `DeviceManager.init_device` for my new device?

It really depends. In my experience yes, if you have a GameDAC. If your device uses a GameDAC v2, it is possible that you can simply copy the Arctis Nova Pro Wireless method, which essentially enables the (otherwise missing) mixer functionality. The packets sent by that manager have been recorded using WireShark listening on the USB interface and I'm unsure whether all of them are required or not. If one or more features are missing to your device, you will probably need to tinker with Wireshark (or similar) listening on the USB interfaces and try to figure it out.

# Acknowledgements

Thanks to:
- [birdls](https://github.com/birdybirdonline/) for the [original project](https://github.com/birdybirdonline/Linux-Arctis-7-Plus-ChatMix).
- [Wander Lairson Costa](https://github.com/walac), [mcuee](https://github.com/mcuee) and [Jonas Malaco](https://github.com/jonasmalacofilho) for the [PyUSB](https://github.com/pyusb/pyusb) library
- [lundiasrj](https://github.com/luandiasrj/) for the custom QWidget [QToggle](https://github.com/luandiasrj/QToggle_-_Advanced_QCheckbox_for_PyQT6)

## Need support?

Don't hesitate to [open an issue](https://github.com/elegos/Linux-Arctis-ChatMix/issues).

Please include as many details as possible, for example the otuput of `journalctl --user -b -f -u arctis-pcm`.

You can also run the software in debug mode, for increased output:

```bash
$ systemctl --user stop arctis-pcm.service
$ cd ~/.local/bin
$ python3 ./arctis_chatmix.py -v
# Debug level log will show

# To start again the service in normal mode
[CTRL]+[C]
$ systemctl --user start arctis-pcm.service
```
