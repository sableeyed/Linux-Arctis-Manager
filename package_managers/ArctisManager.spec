Name:           arctis-manager
Version:        %{_version}
Release:        1%{?dist}
Summary:        SteelSeries GG software replacement for Linux to manage Arctis devices

License:        GPL-3.0
URL:            https://github.com/elegos/Linux-Arctis-Manager
Source0:        https://github.com/elegos/Linux-Arctis-Manager/archive/refs/tags/v%{version}.zip
BuildArch:      x86_64

# Dipendenze richieste per il pacchetto
BuildRequires:  bash, wget
Requires:       bash, python3 >= 3.9, pulseaudio-utils

%description
SteelSeries GG software replacement to manage standard and advanced Arctis devices features, like ChatMix, ANC, wireless mode etc.

%prep
echo $(pwd)
wget https://github.com/elegos/Linux-Arctis-Manager/archive/refs/tags/v%{version}.zip -O v%{version}.zip
unzip v%{version}.zip
mv Linux-Arctis-Manager-%{version}/* .
rm -rf Linux-Arctis-Manager-%{version}

%build
# Nothing to do here

%install
# build root cleanup
rm -rf %{buildroot}
mkdir -p %{buildroot}

# execute the install script (with chroot feature)
export CHROOT=%{buildroot}
export PREFIX="/usr/local"
bash install.sh

%files
/usr/local/share/applications/ArctisManager.desktop
/usr/local/bin/arctis-manager
/usr/local/lib/arctis-manager
/usr/lib/udev/rules.d/91-steelseries-arctis.rules
/usr/lib/systemd/user/arctis-manager.service
/usr/share/icons/hicolor/scalable/apps/arctis_manager.svg

%changelog
* Mon Jan 13 2025 Giacomo Furlan <giacomo@giacomofurlan.name> - 1.6.1-1
- First packaged version of the app
