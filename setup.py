#!/usr/bin/env python3

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def find_packages():
    packages = []
    for init_file in (PROJECT_ROOT / 'bridgebot').rglob('__init__.py'):
        package_path = init_file.parent.relative_to(PROJECT_ROOT)
        if 'test' in package_path.parts:
            continue
        packages.append('.'.join(package_path.parts))
    return sorted(packages)


SETUP_KWARGS = {
    'name': 'bridgebot',
    'version': '0.0.1',
    'description': 'A bot that plays contract bridge',
    'author': 'Evan Meikleham and Mason Brothers',
    'packages': find_packages(),
}


def print_metadata(argv):
    metadata_options = {
        '--name': SETUP_KWARGS['name'],
        '--version': SETUP_KWARGS['version'],
        '--description': SETUP_KWARGS['description'],
        '--author': SETUP_KWARGS['author'],
    }
    if len(argv) == 1 and argv[0] in metadata_options:
        print(metadata_options[argv[0]])
        return True
    return False


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if print_metadata(argv):
        return 0

    try:
        from setuptools import setup
    except ModuleNotFoundError:
        print(
            'setuptools is required for build/install commands. '
            'Metadata queries such as --name and --version work without it.',
            file=sys.stderr,
        )
        return 1

    setup(**SETUP_KWARGS)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
