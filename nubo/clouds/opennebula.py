# -*- coding: utf-8 -*-

"""     
    nubo.clouds.opennebula
    ======================

    Support deployments on OpenNebula private clouds.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

from nubo.clouds.base import BaseCloud
from nubo.clouds.base import AVAILABLE_CLOUDS, CLOUDS_MAPPING

class OpenNebula(BaseCloud):
    
    PROVIDER_NAME = 'OPENNEBULA'
    NEEDED_PARAMS = [ 'key', 'secret', 'host', 'port', 'network_id', 'api_version' ]

    def __init__(self, ssh_private_key=None, login_as='root'):
        self.network_id = AVAILABLE_CLOUDS[
            CLOUDS_MAPPING['OPENNEBULA']].pop('network_id')
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
