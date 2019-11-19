from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Total Rounds',
    version='1.0',
    packages=find_packages(),
    url='',
    license='',
    author='Almaz Rafikov',
    author_email='madnessfox@yandex.ru',
    description='',
)