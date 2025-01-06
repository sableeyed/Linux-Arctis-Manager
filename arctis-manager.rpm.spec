Name:       arctis-manager
Version:    1.5
Release:    1%{?dist}
Summary:    SteelSeries Arctis headset devices manager
License:    GNU GPL v3

URL:        https://github.com/elegos/Linux-Arctis-Manager
Requires:   python >= 3.9, pulseaudio-utils

%description
A replacement for SteelSeries GG software, to manage your Arctis device on Linux!

%prep
# Clean for eventual python cache
find . -name "__pycache__" | xargs rm -rf

%build
# nothing in here

%install
./install.sh

%files
/usr/local/bin/arctis-manager
/usr/local/lib/arctis-manager/*
/usr/lib/udev/rules.d/91-steelseries-arctis.rules
/usr/lib/systemd/user/arctis-manager.service

%changelog
# let's skip this for now
