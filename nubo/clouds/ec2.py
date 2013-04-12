# -*- coding: utf-8 -*-

"""     
    nubo.clouds.ec2
    ===============

    Support deployments on Amazon EC2.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

from nubo.clouds.base import BaseCloud

class AmazonEC2(BaseCloud):

    PROVIDER_NAME = 'EC2_US_EAST'

    def get_ssh_key_id(self):
        try:
            key = self.driver.ex_describe_keypairs(self.ssh_key_name)
            return key['keyName']
        except Exception:
            # This key has not been uploaded yet
            return 

    def list_images(self, limit=20, keyword=''):
        ami_images = [ image for image in self.driver.list_images() 
            if 'ami-' in image.id ]

        return [ image for image in ami_images 
            if (keyword.lower() in image.name.lower()) or not keyword ][:limit]

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
