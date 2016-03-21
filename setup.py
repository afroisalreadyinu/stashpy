import os
from setuptools import setup

setup(
    name = "stashpy",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Python 3 alternative to Logstash"),
    install_requires = ['parse', 'tornado<4.3', 'pyyaml'],
    tests_require = ['nose2', 'matplotlib'],
    packages=['stashpy'],
    entry_points = {
        'console_scripts': ['stashpy = stashpy.main:run']
    },
    url = "https://github.com/afroisalreadyinu/stashpy",
)
