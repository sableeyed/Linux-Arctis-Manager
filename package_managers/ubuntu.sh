#!/usr/bin/env bash

set -e

ubuntu_version="25.04"
software_version=""
software_release="1"

while [ $# -gt 0 ]; do
    case "$1" in
        --ubuntu-version)
            ubuntu_version="$2"
            shift 2
        ;;
        --version)
            software_version="$2"
            shift 2
        ;;
        --release)
            software_release="$2"
            shift 2
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
done

if [ -z "${software_version}" ]; then
    echo "--version is required"
    exit 1
fi

script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
deb_build_image_name="arctis-manager-package-builder:ubuntu-${ubuntu_version}"

function setup() {
    # Remove the old docker image
    img=$(docker images|grep "${deb_build_image_name}" | awk '{print $3}')
    if [ -n "${img}" ]; then docker rmi "${deb_build_image_name}"; fi

    # Build the new docker image
    # docker build --no-cache \
    docker build \
        -t "${deb_build_image_name}" \
        --build-arg user_id="$(id -u)" \
        --build-arg group_id="$(id -g)" \
        --build-arg ubuntu_ver="${ubuntu_version}" \
        -f "Dockerfile.ubuntu" .
}

function deb_build() {
    SRC_DIR="$(cd "${SRC_DIR}" && cd .. && pwd)"
    OUTPUT_DIR="${script_dir}/deb/ubuntu-${ubuntu_version}"

    mkdir -p "${OUTPUT_DIR}"

    docker run --rm \
        --env arctis_manager_ver="${software_version}" \
        --env arctis_manager_ver_release="${software_release}" \
        --volume "${OUTPUT_DIR}":/home/build/output \
        --volume "${SRC_DIR}":/home/build/src \
        "${deb_build_image_name}"
}

cd "${script_dir}"

setup
deb_build
