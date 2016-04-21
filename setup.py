import os
from setuptools import setup

dependencies = ['parse>=1.6',
                'tornado<4.3',
                'pyyaml==3.*',
                'pytz==2016.*',
                'python-dateutil==2.5.*',
                'regex==2016.*']
test_dependencies = ['nose2==0.6.*', 'matplotlib==1.5.*']

setup(
    name = "stashpy",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Python 3 alternative to Logstash"),
    install_requires = dependencies,
    tests_require = test_dependencies,
    packages=['stashpy'],
    entry_points = {
        'console_scripts': ['stashpy = stashpy.main:run']
    },
    url = "https://github.com/afroisalreadyinu/stashpy",
)
