#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
import shutil
import subprocess

config = ConfigParser()
config.read(Path(__file__).parent.parent.joinpath('VERSION.ini'))

software_version = config.get('version', 'SOFTWARE')
software_release = config.get('version', 'RELEASE')

test_path = Path(__file__).parent.parent.joinpath('tests')

# Fedora builds
for version in [40, 41, 42]:
    run = subprocess.run(['./fedora_test.sh', '--fedora-version', str(version), '--version', software_version, '--release', software_release], cwd=test_path)
    if run.returncode != 0:
        shutil.rmtree(
            Path(__file__).parent.joinpath(
                'rpm', 'RPMS', 'x86_64', f'arctis-manager-{software_version}-{software_release}.fc{version}.x86_64.rpm'
            ),
            ignore_errors=True,
        )

# Ubuntu builds
for version in ['24.10', '25.04']:
    run = subprocess.run(['./ubuntu_test.sh', '--ubuntu-version', version, '--version', software_version,
                          '--release', f'{software_release}-ubuntu-{version}-amd64'], cwd=test_path)
    if run.returncode != 0:
        shutil.rmtree(
            Path(__file__).parent.joinpath(
                'deb', f'ubuntu-{version}', f'arctis-manager-{software_version}-ubuntu-{version}-{software_release}-amd64.deb'
            ),
            ignore_errors=True,
        )
