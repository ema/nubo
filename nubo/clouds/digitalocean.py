# -*- coding: utf-8 -*-

"""     
    nubo.clouds.digitalocean
    ========================

    Support deployments on DigitalOcean cloud.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

from nubo.clouds.base import BaseCloud

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

