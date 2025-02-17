#!/usr/bin/env bash

set -e

for file in *.sh; do
    if [ "$file" != "run_tests.sh" ]; then
        echo "Running ${file}"
        echo
        ./"${file}" --version tests --release 1
    fi
done

echo
echo
echo "All tests passed"
