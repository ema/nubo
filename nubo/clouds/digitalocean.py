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
        submitted to Digital Ocean. We use libcloud's 
        `driver.ex_list_ssh_keys` in order to find it out. 

        Return None if the SSH key still has to be uploaded."""
        uploaded_key = [ key.id for key in self.driver.ex_list_ssh_keys() 
            if key.name == self.ssh_key_name ]

        if uploaded_key:
            return str(uploaded_key[0])
        
    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        """Digital Ocean needs the following information: VM size, image, name,
        location and SSH key id.
        
        First, we check if our SSH key is already uploaded on Digital Ocean's
        cloud. If not, we upload it using libcloud's `driver.ex_create_ssh_key`. 
        Then, we call `self.startup` with the required arguments."""
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
