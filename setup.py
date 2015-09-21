from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='sample',
        version='0.7.3',
        description='STEP MOTOR 28BYJ-48 driver for Raspberry Pi',
        long_description=long_description,
        url='https://github.com/Subc2/RPiStepMotor',
        author='Paweł Zacharek',
        author_email='subc2@wp.pl',
        license='GPLv2+',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development',
            'Topic :: System :: Hardware',
            'Topic :: System :: Hardware :: Hardware Drivers',
            'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        ],
        keywords='gpio motor rpi raspberry',
        packages=find_packages(),
        install_requires=['math','RPi','threading','time'],
#       extras_require={},
)
