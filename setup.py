"""
nubo
----
An easy way to deploy Linux VMs on different cloud providers.
"""

from setuptools import setup

setup(
    name='nubo',
    version='0.1',
    url='https://github.com/ema/nubo',
    license='BSD',
    author='Emanuele Rocca',
    author_email='ema@linux.it',
    description='Virtual Machine deployments on multiple cloud providers',
    long_description=__doc__,
    install_requires=[ 
        'setuptools', 
        'apache-libcloud', 
        'paramiko', 
        'texttable' 
    ],
    packages=['nubo'],
    scripts=['scripts/nubo'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: System',
    ],
    keywords='cloud vm startup devops ec2 rackspace',
)
