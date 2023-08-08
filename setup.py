# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='pageviews',
    version='0.0.1',
    description='Wrapper for PageViews API',
    long_description=readme,
    author='Clara Tian',
    url='https://github.com/claratian/pageviews',
    packages=find_packages(exclude=('tests'))
)
