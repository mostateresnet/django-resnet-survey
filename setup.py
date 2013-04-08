import os
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-resnet-survey',
    version='0.1',
    description='Very simple survey app made with django',
    long_description=read('README.md'),
    author='ResNet, Missouri State University',
    author_email='resnet@missouristate.edu',
    license='MIT',
    url='https://github.com/mostateresnet/django-resnet-survey',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ],
    zip_safe=False,
    install_requires=[
        'django-autofixture',
        'qrcode',
        'xlwt',
    ],
    setup_requires=[
        'versiontools >= 1.6',
    ],
)
