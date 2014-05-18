# -*- coding: utf-8 -*-

"""     
    nubo.clouds.base
    ================

    Support deployments on multiple cloud providers.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

import sys
import time
import socket
import logging
import hashlib

from importlib import import_module

from os import getenv
from os.path import join

from libcloud.compute.types import Provider, InvalidCredsError
from libcloud.compute.providers import get_driver

import paramiko

from nubo.config import read_config
from nubo.remote import RemoteHost

CLOUDS_MAPPING = {
    'EC2_US_EAST':        'nubo.clouds.ec2.AmazonEC2', 
    'EC2_US_WEST':        'nubo.clouds.ec2.AmazonEC2', 
    'EC2_US_WEST_OREGON': 'nubo.clouds.ec2.AmazonEC2', 
    'EC2_AP_SOUTHEAST':   'nubo.clouds.ec2.AmazonEC2', 
    'EC2_AP_SOUTHEAST2':  'nubo.clouds.ec2.AmazonEC2', 
    'EC2_AP_NORTHEAST':   'nubo.clouds.ec2.AmazonEC2', 
    'EC2_EU_WEST':        'nubo.clouds.ec2.AmazonEC2',
    'RACKSPACE':          'nubo.clouds.rackspace.Rackspace',
    'RACKSPACE_UK':       'nubo.clouds.rackspace.Rackspace',
    'DIGITAL_OCEAN':      'nubo.clouds.digitalocean.DigitalOcean',
    'LINODE':             'nubo.clouds.linode.Linode',
    'OPENNEBULA':         'nubo.clouds.opennebula.OpenNebula',
}

NODE_STATES = {
    0: 'RUNNING',
    1: 'REBOOTING',
    2: 'TERMINATED',
    3: 'PENDING',
    4: 'UNKNOWN'
}

AVAILABLE_CLOUDS = read_config()

def node2dict(node):
    """Convert a node object into a dict"""
    fields = ( 'id', 'name', 'state', 'public_ips', 
               'private_ips', 'image', 'size', 'extra' )
    values = {}
    for field in fields:
        value = getattr(node, field)
        if value is not None:
            values[field] = value

    values['state'] = NODE_STATES[values['state']]

    for field in 'image', 'size':
        if field in values and values[field]:
            values[field] = values[field].name

    for field in 'public_ips', 'private_ips':
        try:
            values[field] = [ ip_addr.address for ip_addr in values[field] ]
        except AttributeError:
            pass

    return values

def supported_clouds():
    return CLOUDS_MAPPING.keys()

def get_cloud(cloud_name=None):
    """Return a class representing the given cloud provider.

    eg: get_cloud(cloud_name='EC2_US_WEST_OREGON') 
            -> <class 'nubo.clouds.ec2.AmazonEC2'>
    """
    if cloud_name is None:
        cloud_name = getenv('NUBO_CLOUD')

    if cloud_name not in supported_clouds():
        print "E: The NUBO_CLOUD environment variable should be set to one of the following values:"
        print ", ".join(supported_clouds())
        sys.exit(1)


    # fullname = [ 'nubo', 'clouds', 'ec2', 'EC2Cloud' ]
    fullname = CLOUDS_MAPPING[cloud_name].split('.')

    # classname = 'EC2Cloud'
    classname = fullname.pop()

    # module_name = 'nubo.clouds.ec2'
    module_name = '.'.join(fullname)

    module = import_module(module_name)

    cloudclass = getattr(module, classname)
    cloudclass.PROVIDER_NAME = cloud_name

    return cloudclass

class BaseCloud(object):

    # Wait a maximum of 5 minutes
    MAX_ATTEMPTS = 5 * 60
   
    # Has to be set by extending classes
    PROVIDER_NAME = None

    # Can be extended
    NEEDED_PARAMS = [ 'key', 'secret' ]

    @classmethod
    def test_conn(cls, **params):
        provider = getattr(Provider, cls.PROVIDER_NAME)
        DriverClass = get_driver(provider)
        driver = DriverClass(**params)
        try:
            return type(driver.list_nodes()) == list
        except InvalidCredsError:
            return False

    def __init__(self, ssh_private_key=None, login_as='root'):
        if ssh_private_key is None:
            ssh_private_key = join(getenv('HOME'), '.ssh', 'id_rsa')

        self.ssh_private_key = ssh_private_key
        self.ssh_public_key = ssh_private_key + '.pub'

        # Use public key's MD5 sum as its name
        key_hash = hashlib.md5()
        key_hash.update(open(self.ssh_public_key).read())
        self.ssh_key_name = key_hash.hexdigest()
        
        self.login_as = login_as

        try:
            provider = getattr(Provider, self.PROVIDER_NAME)
        except AttributeError:
            raise Exception, "Unknown cloud %s" % self.PROVIDER_NAME

        DriverClass = get_driver(provider)
        self.driver = DriverClass(
            **AVAILABLE_CLOUDS[CLOUDS_MAPPING[self.PROVIDER_NAME]])

    def __wait_for_node(self, node_id):
        attempts = self.MAX_ATTEMPTS

        while attempts:
            for node in self.list_nodes():
                if node['id'] != node_id: 
                    continue

                if node['state'] == "RUNNING":
                    return node
                
                logging.info("%s attempts left on %s: %s != RUNNING" % (
                    attempts, node_id, node['state']))
            
            time.sleep(1)
            attempts -= 1

    def wait_for_ssh(self, node):
        attempts = self.MAX_ATTEMPTS
        remotehost = RemoteHost(node['public_ips'][0], self.ssh_private_key)

        while attempts:
            try:
                return remotehost.whoami(self.login_as)
            except socket.error:
                logging.info("%s SSH attempts left for user %s on %s" 
                    % (attempts, self.login_as, node['id']))

                time.sleep(1)
                attempts -= 1
            except paramiko.PasswordRequiredException:
                msg = 'Authentication failed for %s@%s. ' % (
                    self.login_as, node['id'])
                msg += 'Perhaps you should login as a different user?'
                raise Exception(msg)

    def startup(self, params):
        """Start a new instance.

        Each cloud provider requires different values here. 

        'name', 'image', and 'size' are the lowest common denominator.

        eg: startup(params) -> dict
        """
        # Start a new VM and keep track of its ID
        node_id = node2dict(self.driver.create_node(**params))['id']

        # Wait for the VM to be RUNNING
        node = self.__wait_for_node(node_id)
        assert node is not None

        # Wait for SSH connections to be accepted
        user = self.wait_for_ssh(node)
        assert user == self.login_as

        return node

    def is_running(self, node_id):
        """Return True if the given node is running."""
        running_ids = [
            node2dict(node)['id'] for node in self.driver.list_nodes() 
        ]

        return node_id in running_ids

    def __call_if_running(self, function, node_id):
        if not self.is_running(node_id):
            return False

        class Node:
            id = node_id

        return function(Node)
        
    def shutdown(self, node_id):
        """Shutdown the given instance id.
        
        eg: shutdown('i-bb6c3b88') -> bool
        """
        return self.__call_if_running(self.driver.destroy_node, node_id)

    def reboot(self, node_id):
        """Reboot the given instance id.
        
        eg: reboot('i-bb6c3b88') -> bool
        """
        return self.__call_if_running(self.driver.reboot_node, node_id)

    def list_nodes(self):
        """Return a list of dictionaries representing currently running
        nodes."""
        return [ node2dict(node) for node in self.driver.list_nodes() ]

    def list_sizes(self):
        """Return a list of strings representing the available instance
        size names."""
        return [ size.name for size in self.driver.list_sizes() ]

    def list_images(self, limit=None, keyword=''):
        """Return a list of VM images available on this cloud."""
        images = [ image for image in self.driver.list_images() 
            if (keyword.lower() in image.name.lower()) or not keyword ]

        if limit:
            return images[:limit]

        return images

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        """Deploy a VM instance on this cloud. This method is not implemented
        here, it has to be specialized by the classes implementing specific 
        cloud providers."""
        raise NotImplementedError()
