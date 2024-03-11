"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from myplugin import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='scipion-em-template',  # Required
    version=__version__,  # Required
    description='Scipion plugin template.',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/scipion-em/scipion-em-myplugin',  # Optional
    author='you',  # Optional
    author_email='you@yourinstitution.email',  # Optional
    keywords='scipion cryoem imageprocessing scipion-3.0',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(),
    install_requires=[requirements],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/scipion-em/scipion-em-template/issues',
        'Source': 'https://github.com/scipion-em/scipion-em-template/',
    },
    entry_points={'pyworkflow.plugin': 'myplugin = myplugin'},
    package_data={  # Optional
       'myplugin': ['icon.png', 'protocols.conf'],
    }
)
