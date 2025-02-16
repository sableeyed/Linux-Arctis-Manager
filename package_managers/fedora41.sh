#!/usr/bin/env bash

set -e

software_version=""
software_release="1"

while [ $# -gt 0 ]; do
    case "$1" in
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
rpm_build_image_name="arctis-manager-package-builder-fedora-41"

function setup() {
    # Remove the old docker image
    img=$(docker images|grep "${rpm_build_image_name}" | awk '{print $3}')
    if [ -n "${img}" ]; then docker rmi "${rpm_build_image_name}"; fi

    # Build the new docker image
    docker build --no-cache \
        -t "${rpm_build_image_name}" \
        --build-arg user_id="$(id -u)" \
        --build-arg group_id="$(id -g)" \
        -f Dockerfile.fedora41 .
}

function rpm_build() {
    RPMS_DIR="${script_dir}/rpm/RPMS"
    SRPMS_DIR="${script_dir}/rpm/SRPMS"
    SRC_DIR="$(cd "${SRC_DIR}" && cd .. && pwd)"

    if [ -d "${RPMS_DIR}" ]; then
        rm -rf "${RPMS_DIR}"
    fi
    mkdir -p "${RPMS_DIR}" "${SRPMS_DIR}"

    docker run --rm \
        --env arctis_manager_ver="${software_version}" \
        --env arctis_manager_ver_release="${software_release}" \
        --volume "${RPMS_DIR}":/home/build/rpmbuild/RPMS \
        --volume "${SRPMS_DIR}":/home/build/rpmbuild/SRPMS \
        --volume "${SRC_DIR}":/home/build/src \
        arctis-manager-package-builder-fedora-41
}

cd "${script_dir}"

setup
rpm_build
