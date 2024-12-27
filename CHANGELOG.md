# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1]

### Changed

- Little optiomization: avoid checking / kernel detaching same interfaces multiple times.

### Fixed

- Fixed systemd's service immediate shutdown, provoked by kernel detach. The service will now gracefully stop when the device is being disconnected
