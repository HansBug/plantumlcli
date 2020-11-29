import os
from codecs import open
from distutils.core import setup

from setuptools import find_packages

_package_name = 'plantumlcli'
here = os.path.abspath(os.path.dirname(__file__))
meta = {}
with open(os.path.join(here, _package_name, 'config', 'meta.py'), 'r', 'utf-8') as f:
    exec(f.read(), meta)

with open('requirements.txt', 'r', 'utf-8') as f:
    _lines = f.readlines()
    requirements = [line.strip() for line in _lines if line.strip()]

with open('requirements-test.txt', 'r', 'utf-8') as f:
    _lines = f.readlines()
    requirements_dev = [line.strip() for line in _lines if line.strip()]

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

_package_version = meta['__VERSION__']
setup(
    name=meta['__TITLE__'],
    version=_package_version,
    description=meta['__DESCRIPTION__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(
        include=(_package_name, "%s.*" % _package_name)
    ),
    author=meta['__AUTHOR__'],
    author_email=meta['__AUTHOR_EMAIL__'],
    python_requires=">=3.5",
    install_requires=requirements,
    tests_require=requirements_dev,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    include_package_data=True,
    project_urls={
        'Documentation': 'https://github.com/HansBug/plantumlcli/blob/main/README.md',
        'Source': 'https://github.com/HansBug/plantumlcli',
        "Issue tracker": "https://github.com/HansBug/plantumlcli/issues",
    },
    entry_points={
        'console_scripts': [
            'plantumlcli=plantumlcli.entrance.cli:cli'
        ]
    },
)
