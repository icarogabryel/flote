from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('LICENSE.md', 'r') as f:
    license_text = f.read()

setup(
    name='flote',
    version='0.1.0',
    author='Ícaro Gabryel',
    author_email='icarogabryel2001@gmail.com',
    packages=['flote'],
    description=(
        'Flote is a HDL and Python framework for simulation. '
        'Designed to be friendly, simple, and productive. Easy to use and learn.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/icarogabryel/flote',
    license=license_text,
    keywords='HDL, simulation, Python, framework, friendly, simple, productive',
)
