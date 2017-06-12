#!/usr/bin/python
__version__ = '1.0'

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README')) as f:
    README = f.read()

install_requires = []
# with open(os.path.join(here, 'requirements.txt')) as fd:
with open(os.path.join(here, 'requirements-mongodb.txt')) as fd:
    for dep in [line.strip() for line in fd.read().split('\n')]:
        install_requires.append(dep)

setup(
    name='IMAgent',
    version=__version__,
    description='this is an iMonitor module',
    long_description=README + '\n\n',
    author='hzluqianjie',
    author_email='240580250@.com',
    url='www.zuiyuemuai.com',
    license='MIT',
    data_files=[('/etc/IMAgent', ['imagent/conf/agent.cnf','imagent/conf/logging.cnf'])],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'imagent = imagent.entrypoint:run',
        ]
    },

    zip_safe=False,
    install_requires=install_requires,
)