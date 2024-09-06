#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="kingronjan",
    author_email='kingronjan@qq.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A better patch tool for python test.",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='wonderpatch',
    name='wonderpatch',
    packages=find_packages(include=['wonderpatch', 'wonderpatch.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kingronjan/wonderpatch',
    version='0.1.0',
    zip_safe=False,
)
