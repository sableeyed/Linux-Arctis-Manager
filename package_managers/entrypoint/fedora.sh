#!/usr/bin/env bash

rpmbuild \
    --define "_version ${arctis_manager_ver}" \
    --define "_release ${arctis_manager_ver_release}" \
    --define '_localbuild 1' \
    --define '_sourcedir /home/build/src' \
    -ba package_managers/ArctisManager.spec
