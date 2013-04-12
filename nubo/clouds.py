# -*- coding: utf-8 -*-

"""     
    nubo.clouds
    ===========

    Support deployments on multiple cloud providers.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

import time
import socket
import logging
import hashlib

from os import getenv
from os.path import join

from libcloud.compute.types import Provider, InvalidCredsError
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment

from remote import RemoteHost
from config import read_config

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
        if 'field' in values and values[field]:
            values[field] = values[field].name

    for field in 'public_ips', 'private_ips':
        try:
            values[field] = [ ip_addr.address for ip_addr in values[field] ]
        except AttributeError:
            pass

    return values

def supported_clouds():
    supported = []

    for candidate in globals().values():
        if type(candidate) is not type:
            # We only want classes
            continue
    
        if not issubclass(candidate, BaseCloud):
            # Sub-classes of BaseCloud
            continue

        if candidate is BaseCloud:
            # But not BaseCloud itself
            continue

        supported.append(candidate)

    return supported

class BaseCloud(object):

    # Wait a maximum of 5 minutes
    MAX_ATTEMPTS = 5 * 60
   
    # Has to be set by extending classes
    PROVIDER_NAME = None

    # Can be extended
    NEEDED_PARAMS = [ 'key', 'secret' ]

    @classmethod
    def test_conn(cls, key, secret):
        provider = getattr(Provider, cls.PROVIDER_NAME)
        DriverClass = get_driver(provider)
        driver = DriverClass(key, secret)
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
            raise Exception, "Unknown cloud %s" % PROVIDER_NAME

        DriverClass = get_driver(provider)
        self.driver = DriverClass(**AVAILABLE_CLOUDS[self.PROVIDER_NAME])

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

    def __wait_for_ssh(self, node):
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

    def startup(self, params):
        """Start a new instance.

        Each cloud provider requires different values here. 

        'name', 'image', and 'size' are the lowest common denominator.

        eg: startup(params) -> Node
        """
        # Start a new VM and keep track of its ID
        node_id = node2dict(self.driver.create_node(**params))['id']

        # Wait for the VM to be RUNNING
        node = self.__wait_for_node(node_id)
        assert node is not None

        # Wait for SSH connections to be accepted
        user = self.__wait_for_ssh(node)
        assert user == self.login_as

        return node

    def is_running(self, node_id):
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
        return [ node2dict(node) for node in self.driver.list_nodes() ]

    def list_images(self, limit=20):
        return self.driver.list_images()[:limit]

    def deploy(self, size_idx=0, location_idx=0, name='test'):
        raise NotImplementedError()

class Rackspace(BaseCloud):

    PROVIDER_NAME = 'RACKSPACE'

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        sd = SSHKeyDeployment(open(self.ssh_public_key).read())
        script = ScriptDeployment("/bin/true") # NOP
        msd = MultiStepDeployment([sd, script])

        class Image:
            id = image_id

        size = self.driver.list_sizes()[size_idx]
        location = self.driver.list_locations()[location_idx]

        return node2dict(self.driver.deploy_node(name=name, image=Image, 
            size=size, location=location, deploy=msd))

class DigitalOcean(BaseCloud):

    PROVIDER_NAME = 'DIGITAL_OCEAN'

    def get_ssh_key_id(self):
        """Return uploaded key id if this SSH public key has been already
        submitted to the cloud provider. None otherwise."""
        uploaded_key = [ key.id for key in self.driver.ex_list_ssh_keys() 
            if key.name == self.ssh_key_name ]

        if uploaded_key:
            return str(uploaded_key[0])
        
    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        key_id = self.get_ssh_key_id()

        if not key_id:
            uploaded_key = self.driver.ex_create_ssh_key(self.ssh_key_name, 
                open(self.ssh_public_key).read())

            key_id = str(uploaded_key.id)

        class Image:
            id = image_id

        size = self.driver.list_sizes()[size_idx]
        location = self.driver.list_locations()[location_idx]
        
        return self.startup({ 
            'size': size, 'image': Image, 'name': name,
            'location': location, 'ex_ssh_key_ids': [ key_id ]
        })

class EC2Cloud(BaseCloud):

    PROVIDER_NAME = 'EC2_US_EAST'

    def get_ssh_key_id(self):
        try:
            key = self.driver.ex_describe_keypairs(self.ssh_key_name)
            return key['keyName']
        except Exception:
            # This key has not been uploaded yet
            return 

    def list_images(self, limit=20):
        return [ image for image in self.driver.list_images() 
            if 'ami-' in image.id ][:limit]

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        # Uploading SSH key if necessary
        key_id = self.get_ssh_key_id()

        if not key_id:
            key = self.driver.ex_import_keypair(self.ssh_key_name,
                self.ssh_public_key)

            key_id = key['keyName']

        # Creating security group if necessary
        if __name__ not in self.driver.ex_list_security_groups():
            self.driver.ex_create_security_group(__name__, "nubolib's SG")
            self.driver.ex_authorize_security_group_permissive(__name__)

        class Image:
            id = image_id

        size = self.driver.list_sizes()[size_idx]
        location = self.driver.list_locations()[location_idx]
        
        return self.startup({ 
            'size': size, 'image': Image, 'name': name,
            'location': location, 'ex_keyname': key_id,
            'ex_securitygroup': __name__
        })

class OpenNebula(BaseCloud):
    
    PROVIDER_NAME = 'OPENNEBULA'

    def __init__(self, ssh_private_key=None):
        self.network_id = AVAILABLE_CLOUDS['OPENNEBULA'].pop('network_id')
        BaseCloud.__init__(self, ssh_private_key)

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        script = """#!/bin/bash
dhclient eth0

# assiging IP
. /mnt/context.sh
ip addr add dev eth0 $IP_PUBLIC

# removing IP obtained from DHCP
ip addr del dev eth0 `ip addr show dev eth0 | awk '/inet 192/ { print $2 ; exit }'`

# adding ssh_key_file
mkdir ~%s/.ssh || true
cat <<EOF >~%s/.ssh/authorized_keys
%s
EOF
""" % (self.login_as, self.login_as, open(self.ssh_public_key).read())

        size = self.driver.list_sizes()[size_idx]

        class Image:
            id = image_id

        class Network:
            id = self.network_id
            address = None

        context = { 
            'USERDATA': script.encode('hex'),
            'IP_PUBLIC': '$NIC[IP]'
        }
        return self.startup({ 'size': size, 'image': Image, 
                              'networks': Network, 'name': name,
                              'context': context })
