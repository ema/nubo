"""
nubo
----
An easy way to deploy Linux VMs on different cloud providers.

Links
`````
* `GitHub Repository <https://github.com/ema/nubo>`_
* `Development Version
  <http://github.com/ema/nubo/zipball/master#egg=nubo-dev>`_
"""

from setuptools import setup

install_requires = [ 
        'setuptools', 
        'apache-libcloud', 
        'paramiko', 
        'texttable' 
]

try:
    import importlib
except ImportError:
    install_requires.append('importlib')

setup(
    name='nubo',
    version='0.7',
    url='http://pythonhosted.org/nubo',
    license='BSD',
    author='Emanuele Rocca',
    author_email='ema@linux.it',
    description='Virtual Machine deployments on multiple cloud providers',
    long_description=__doc__,
    install_requires=install_requires,
    packages=['nubo', 'nubo.clouds'],
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
    keywords='cloud vm startup devops ec2 rackspace linode',
)
