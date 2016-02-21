import os
from setuptools import setup

dependencies = ['parse', 'tornado<4.3', 'tornadoes', 'nose2', 'pyyaml']

setup(
    name = "stashpy",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Python 3 alternative to Logstash"),
    install_requires = dependencies,
    packages=['stashpy'],
    entry_points = {
        'console_scripts': ['stashpy = stashpy.main:run']
    },
    url = "https://github.com/afroisalreadyinu/stashpy",
)
