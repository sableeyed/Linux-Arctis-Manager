#!/usr/bin/env bash

set -e

deb_name="arctis-manager-${arctis_manager_ver}-${arctis_manager_ver_release}"

output_dir="/home/build/output"
root_dir="/home/build/build"
src_dir="/home/build/src"
build_root_dir="${root_dir}/build"
build_dir="${build_root_dir}/${deb_name}"
debian_dir="${build_dir}/DEBIAN"

install_prefix=/usr/local
chroot="${build_dir}"

mkdir -p "${build_dir}"
mkdir -p "${debian_dir}"

cd "${src_dir}"
PREFIX="${install_prefix}" CHROOT="${chroot}" ./install.sh

cd "${build_root_dir}"
chmod -R 755 "${debian_dir}"
cp "${src_dir}/package_managers/ArctisManager.control" "${debian_dir}/control"
# Use sed instead of perl
sed -i "s/Version: .*/Version: ${arctis_manager_ver}-${arctis_manager_ver_release}/" "${debian_dir}/control"
dpkg-deb --build "${deb_name}"

cp "${deb_name}.deb" "${output_dir}"

# Build the deb package using dpkg-deb
dpkg-deb --build "${deb_name}"

# Copy the resulting .deb package to the output directory
cp "${deb_name}.deb" "${output_dir}"
