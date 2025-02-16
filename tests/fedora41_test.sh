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

# 1. Build the rpm archives
../package_managers/fedora41.sh --version "${software_version}" --release "${software_release}"

# 2. Install the package and try to run the application in a clean container.
# It is expected to exit with exit code 101 (device not found). Otherwise the test will fail.

# Extra dependencies are required to run an x11 server within docker
set +e
docker build --tag arctis-manager-test:fc41 -f Dockerfile.fedora41 .
docker run --rm \
    --volume "$(pwd)/../package_managers/rpm/RPMS":/rpms \
    arctis-manager-test:fc41 \
    bash -c ' \
        Xvfb :99 -screen 0 640x480x8 -nolisten tcp & xvfb_pid=$!; \
        trap "kill $xvfb_pid" EXIT; \
        sudo dnf install -y /rpms/x86_64/arctis-manager-*.rpm \
        && LANG=en_US.UTF-8 arctis-manager --verbose --daemon-only; \
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
