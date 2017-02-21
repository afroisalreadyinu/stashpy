import os
from setuptools import setup

dependencies = ['parse>=1.6',
                'tornado<4.3',
                'pyyaml>=3.0',
                'pytz>=2016',
                'python-dateutil>=2.5',
                'regex>=2016']
test_dependencies = ['nose2>=0.6', 'matplotlib>=1.5']

setup(
    name = "stashpy",
    version = "0.03",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Python 3 alternative to Logstash"),
    install_requires = dependencies,
    tests_require = test_dependencies,
    packages=['stashpy'],
    package_data={'stashpy': ['stashpy/patterns/*.dat']},
    entry_points = {
        'console_scripts': ['stashpy = stashpy.main:run']
    },
    url = "https://github.com/afroisalreadyinu/stashpy",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords = 'logging elasticsearch kibana monitoring',
)
