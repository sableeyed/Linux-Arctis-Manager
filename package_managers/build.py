#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
import subprocess

config = ConfigParser()
config.read(Path(__file__).parent.parent.joinpath('VERSION.ini'))

software_version = config.get('version', 'SOFTWARE')
software_release = config.get('version', 'RELEASE')

test_path = Path(__file__).parent.parent.joinpath('tests')

# Fedora builds
for version in [40, 41]:
    subprocess.run(['./fedora_test.sh', '--fedora-version', str(version), '--version', software_version, '--release', software_release], cwd=test_path)

# Ubuntu builds
# LTS version
for version in ['24.04.1', '24.10', '25.04']:
    subprocess.run(['./ubuntu_test.sh', '--ubuntu-version', version, '--version', software_version,
                   '--release', f'ubuntu-{version}-{software_release}'], cwd=test_path)
