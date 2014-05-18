Nubo
====

.. image:: https://secure.travis-ci.org/ema/nubo.png?branch=master
   :target: http://travis-ci.org/ema/nubo 

.. module:: nubo

`Nubo` is a command line program that allows you to start virtual machines on
different cloud providers, also making sure you can SSH into those instances
once they are available. 

As an example, you might want to start a new node on Amazon EC2::

    $ export NUBO_CLOUD=EC2_EU_WEST
    $ nubo start ami-27013f53
    Instance i-4ea89004 available on EC2_EU_WEST. Public IP: 54.247.8.150

And then install puppet on it::

    $ ssh root@54.247.8.150 "apt-get -y install puppet"
    Warning: Permanently added '54.247.8.150' (RSA) to the list of known hosts.
    Reading package lists...
    Building dependency tree...
    Reading state information...
    The following extra packages will be installed:
    [...]

One of the biggest challenges when deploying virtual machines on multiple
clouds is ensuring you can actually access those machines after they have
started up. For example, different cloud providers allow you to upload your SSH
public key in different ways. Certain providers automatically configure
firewall rules which by default deny traffic to your instances. If your
deployments need to be automated, your infrastructure code has to deal with
that.

`nubo` abstracts away these differences for you. It uses `Apache Libcloud`_ to
start virtual machines on different cloud providers and `Paramiko`_ to
establish SSH connections to the instances you start. Its functionalities are
also available as a Python library.

.. _Apache Libcloud: https://libcloud.apache.org/
.. _Paramiko: http://www.lag.net/paramiko/

Installation
------------

Install `nubo` with one of the following commands::

    $ pip install nubo

Alternatively, use `easy_install`::

    $ easy_install nubo

You need to have `ca-certificates`_ installed on your system.

.. _ca-certificates: https://wiki.apache.org/incubator/LibcloudSSL#Enabling_SSL_Certificate_Check

Usage
-----

Invoke `nubo` without arguments to see the available functionalities::

    $ nubo
    usage: nubo [-h] {config,clouds,list,images,start,reboot,delete} ...

    Start Virtual Machines on multiple clouds

    positional arguments:
      {config,clouds,list,images,start,reboot,delete}
        config              set your cloud credentials
        clouds              list available clouds
        list                list running VMs
        images              list available images
        start               start a new VM
        reboot              reboot a given VM
        delete              delete a given VM

    optional arguments:
      -h, --help            show this help message and exit

Run `nubo config` to set your cloud credentials. The following examples shows
how we can configure one of the available cloud providers::

    $ nubo config
     1 DIGITAL_OCEAN
     2 EC2_AP_NORTHEAST
     3 EC2_AP_SOUTHEAST
     4 EC2_AP_SOUTHEAST2
     5 EC2_EU_WEST
     6 EC2_US_EAST
     7 EC2_US_WEST
     8 EC2_US_WEST_OREGON
     9 OPENNEBULA
    10 RACKSPACE
    11 RACKSPACE_UK
    Please choose the cloud provider you want to setup [1-11] 5
    Please provide your API key: MYAPIKEY
    Please provide your API secret: MYAPISECRET
    EC2_EU_WEST cloud configured properly

To see which virtual machine images are available, we can use `nubo images`::
    
    $ NUBO_CLOUD=DIGITAL_OCEAN nubo images
    20 images available on DIGITAL_OCEAN
     id              name           
    ===============================
    85271   wheezy                  
    85431   postgres-base           
    1607    Gentoo x64              
    13632   Open Suse 12.1 x32      
    13863   Open Suse 12.2 X64      
    18414   Arch Linux 2012-09 x64  
    23593   Arch Linux 2012-09 x64  
    63749   Gentoo 2013-1 x64       
    1601    CentOS 5.8 x64          
    1602    CentOS 5.8 x32          
    1609    Ubuntu 11.10 x32 Server 
    1611    CentOS 6.2 x64          
    1615    Fedora 16 x64 Server    
    1618    Fedora 16 x64 Desktop   
    2676    Ubuntu 12.04 x64 Server 
    12573   Debian 6.0 x64          
    12574   CentOS 6.3 x64          
    12575   Debian 6.0 x32          
    12578   CentOS 6.3 x32          
    14097   Ubuntu 10.04 x64 Server 

New virtual machine instances can be started with `nubo start`. Note that the
command will not return until the remote machine has finished booting up and
it accepts SSH connections::

    $ nubo start DIGITAL_OCEAN 12573
    Instance 150843 available on DIGITAL_OCEAN. Public IP: 198.199.72.211

With `nubo list` we can see the status of our virtual machines on a given cloud
provider::
     
    $ nubo list DIGITAL_OCEAN 
    1 VMs running on DIGITAL_OCEAN
      id     name    state          ip       
    ========================================
    150843   test   RUNNING   198.199.72.211 

API Reference
-------------
All `nubo` functionalities can be accessed via its Python API. Here is a brief
example of how to deploy a new virtual machine::

    from nubo.clouds.base import get_cloud
    
    Cloud = get_cloud('EC2_EU_WEST')
    ec2 = Cloud()

    print ec2.deploy(image_id='ami-27013f53', name='my-new-vm')

Please refer to the following API documentation for further details.

.. automodule:: nubo.clouds.base
   :members:

.. autoclass:: nubo.clouds.base.BaseCloud
   :show-inheritance:
   :members:

.. automodule:: nubo.clouds.digitalocean
   :members:

.. autoclass:: nubo.clouds.digitalocean.DigitalOcean
   :show-inheritance:
   :members:

.. automodule:: nubo.clouds.ec2
   :members:

.. autoclass:: nubo.clouds.ec2.AmazonEC2
   :show-inheritance:
   :members:

.. automodule:: nubo.clouds.rackspace
   :members:

.. autoclass:: nubo.clouds.rackspace.Rackspace
   :show-inheritance:
   :members:

.. automodule:: nubo.clouds.opennebula
   :members:

.. autoclass:: nubo.clouds.opennebula.OpenNebula
   :show-inheritance:
   :members:
