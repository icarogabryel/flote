"""
This is the setup.py file for the Flote package.
It is used to package and distribute the Flote library.
"""
from setuptools import setup

from flote.model.component import VERSION


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='flote',
    version=VERSION,
    author='Ícaro Gabryel',
    author_email='icarogabryel2001@gmail.com',
    packages=['flote'],
    description=(
        'Flote is a HDL and Python framework for simulation. Designed to be'
        'friendly, simple, and productive. Easy to use and learn.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/icarogabryel/flote',
    license='GPL-3.0',
    keywords=[
        'HDL',
        'simulation',
        'Python',
        'framework',
        'friendly',
        'simple',
        'productive'
    ],
)
