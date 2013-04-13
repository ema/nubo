# -*- coding: utf-8 -*-

"""     
    nubo.clouds.rackspace
    =====================

    Support deployments on Rackspace cloud.

    :copyright: (C) 2013 by Emanuele Rocca.
"""

from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment
from libcloud.compute.deployment import SSHKeyDeployment

from nubo.clouds.base import BaseCloud, node2dict

class Rackspace(BaseCloud):

    PROVIDER_NAME = 'RACKSPACE' 

    def deploy(self, image_id, size_idx=0, location_idx=0, name='test'):
        """Rackspace supports libcloud's `libcloud.compute.deployment`.

        Pass an `SSHKeyDeployment` to `self.driver.deploy_node`."""
        sd = SSHKeyDeployment(open(self.ssh_public_key).read())
        script = ScriptDeployment("/bin/true") # NOP
        msd = MultiStepDeployment([sd, script])

        class Image:
            id = image_id

        size = self.driver.list_sizes()[size_idx]
        location = self.driver.list_locations()[location_idx]

        return node2dict(self.driver.deploy_node(name=name, image=Image, 
            size=size, location=location, deploy=msd))
