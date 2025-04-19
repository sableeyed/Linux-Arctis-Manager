# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.3]

### Added

- Package build script for (Fedora, Ubuntu)
- Distro-specific docker-based tests, to test in clean environments (Fedora, Ubuntu)
- [Build script](./package_managers/build.py) to build all supported packages (experimental)
- arctis-manager: added --daemon-only option (mainly for test purposes, but can be used to disable the UI)
- VERSION.ini to better store and the version
- Systemd dependencies on graphical.target instead of default.target

### Changed

- In case of device error during the identification process, if something goes wrong, reset the selected device and log the error
- Embedded Qt6/plaform static libraries, generated on OS-basis, to avoid breaking dependencies on qt libs, which might not be distributed otherwise (slightly bigger package)

## [1.6.2]

### Added

- PyInstaller dev dependency to handle pip dependencies
- PyInstaller spec files for both binaries (arctis manager desktop app launcher and daemon)
- VSCode RPM build task

### Changed

- Installer now bundles everything into fewer binary files, instead of installing dependencies in the lib folder

### Fixed

- RPM build

## [1.6.1]

### Fixed

- Prevent service to shutdown on settings window close

## [1.6.0]

### Added

- Settings window
  - device name on top of the layout
  - Dedicated status page on top of the settings
- System tray app:
  - added DBus support for name.giacomofurlan.ArctisManager.ShowSettings()
- Desktop app, which essentially wraps a DBus call to open the settings window

## [1.5.3]

### Fixed

- Fixed Arctis 7 Plus Device Manager (thanks @XiokroDarc)

## [1.5.2]

### Fixed

- Using `QApplication.exec()` instead of `QApplication.exec_()` (which works only on dirty environments)

## [1.5.1]

### Changed

- Quit application on exception of any service (systray app or daemon)
- Gracefully stop services only once (guard check)

### Fixed

- Arctis Pro Wireless: send 64 bytes payload messages, instead of 91

## [1.5]

### Changed

- Project name change from "Arctis ChatMix" to "Arctis Manager" to reflect the wider project goals
- User-agnostic, revamped udev rules
- New install script to install the software in proper prefix

## [1.4]

### Added

- System tray icon with dynamic status, depending on what the device is able to provide via DeviceStatus dataclass
- DeviceStatus for the following devices:
  - Arctis Nova Pro Wireless (and variants)
- Device settings for the following devices:
  - Arctis Nova Pro Wireless (and variants)
- Added translation files (dynamically loaded via LOCALE))

### Changed

- **BREAKING**: `DeviceStatus` has changed

## [1.3.1]

### Fixed

- Fixed Chat audio channels links

## [1.3]

### Added

- Support for libnotify (via `notify-send` command)

## [1.2]

### Added

- Support for Arctis Nova Pro Wireless battery and connection state
- Support for Arctis Nova Pro Wireless X (experimental, should be the same of Nova Pro Wireless, but with different device id)

### Removed

- Arctis Nova Pro Wireless: 'state' commands during device init (`0x06b7`)

## [1.1]

### Changed

- Little optiomization: avoid checking / kernel detaching same interfaces multiple times.

### Fixed

- Fixed systemd's service immediate shutdown, provoked by kernel detach. The service will now gracefully stop when the device is being disconnected
