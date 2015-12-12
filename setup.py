from setuptools import setup, find_packages

setup(
    name='abu',
    description='A Python wrapper around the 2ch.hk API',
    version='0.1',
    url='https://github.com/fbjorn/cuddly-octo-wookie',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='python 2ch api',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests'],
)
