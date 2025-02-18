#!/usr/bin/env bash

set -e

software_version=""
software_release="1"
ubuntu_version="25.04"

script_dir="$(cd "$(dirname "$0")" && pwd)"
cd "${script_dir}"

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

# 1. Build the rpm archives
../package_managers/ubuntu.sh --ubuntu-version "${ubuntu_version}" --version "${software_version}" --release "${software_release}"

# 2. Install the package and try to run the application in a clean container.
# It is expected to exit with exit code 101 (device not found). Otherwise the test will fail.

set +e
docker build --tag "arctis-manager-test:ubuntu-${ubuntu_version}" \
    --build-arg ubuntu_ver="${ubuntu_version}" \
    -f Dockerfile.ubuntu .
docker run --rm \
    --volume "$(pwd)/../package_managers/deb/ubuntu-${ubuntu_version}":/debs \
    "arctis-manager-test:ubuntu-${ubuntu_version}" \
    bash -c ' \
        Xvfb :99 -screen 0 640x480x8 -nolisten tcp & xvfb_pid=$!; \
        trap "kill $xvfb_pid" EXIT; \
        sudo apt install -y /debs/arctis-manager-'"${software_version}"'-'"${software_release}"'.deb \
        && export LANG=en_US.UTF-8 \
        && env \
        && arctis-manager --verbose --daemon-only; \
        exit_code=$?; \
        kill $xvfb_pid; \
        exit $exit_code
    '
exit_code=$?
set -e

if [ $exit_code -ne 101 ]; then
    echo "Test failed. Expected exit code 101, got: $exit_code"

    exit 1
fi
