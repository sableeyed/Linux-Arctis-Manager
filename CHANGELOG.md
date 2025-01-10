# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
