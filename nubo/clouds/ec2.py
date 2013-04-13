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
        """Return uploaded key id if this SSH public key has been already
        submitted to Amazon EC2. We use libcloud's `driver.ex_describe_keypairs` 
        in order to find it out. 

        Return None if the SSH key still has to be uploaded."""
        try:
            key = self.driver.ex_describe_keypairs(self.ssh_key_name)
            return key['keyName']
        except Exception:
            # This key has not been uploaded yet
            return 

    def list_images(self, limit=20, keyword=''):
        """Amazon also returns kernel-related info in `driver.list_images`. We
        do not care about kernels here, only about bootable VM images (AMIs).

        First, we get the list of available AMIs. Then, we search for the
        user-specified keyword (if any). 

        Only 20 results are returned by default to avoid flooding users with
        too much output."""
        ami_images = [ image for image in self.driver.list_images() 
            if 'ami-' in image.id ]

        if not limit:
            limit = 20

        return [ image for image in ami_images 
            if (keyword.lower() in image.name.lower()) or not keyword ][:limit]

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        """Amazon EC2 needs the following information: VM size, image, name,
        location, SSH key name and security group name.
        
        First, we check if our SSH key is already uploaded on Amazon's cloud.
        If not, we upload it using libcloud's `driver.ex_import_keypair`. 

        Then, we create a permissive Security Group with
        `driver.ex_create_security_group` and
        `driver.ex_authorize_security_group_permissive`.

        Finally, we call `self.startup` with the required arguments."""
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
