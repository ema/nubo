nubo
====

.. module:: nubo

nubo is a command line program which allows you to start virtual machines on
different cloud providers.

Its functionalities are also available as a Python library.

Installation
------------

Install the extension with one of the following commands::

    $ pip install nubo

Alternatively, use `easy_install`::

    $ easy_install nubo

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

To see which virtual machine images we have available, we can use `nubo
images`::
    
    $ nubo images DIGITAL_OCEAN
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

.. autoclass:: nubo
   :members:

