# -*- coding: utf-8 -*-

from nubo.clouds import base

from nubo.clouds.ec2 import AmazonEC2
from nubo.clouds.opennebula import OpenNebula

import unittest

class DummyCloud(base.BaseCloud):
    """Dummy cloud using the DUMMY libcloud provider"""
    PROVIDER_NAME = 'DUMMY'

    def __wait_for_ssh(self, node):
        return 'root'
    
class BaseTest(unittest.TestCase):

    def test_supported_clouds(self):
        self.failUnless(base.supported_clouds())

        for cloud in base.supported_clouds():
            self.assertEquals(str, type(cloud))

    def test_get_cloud(self):
        ec2 = base.get_cloud('EC2_AP_SOUTHEAST2')
        self.assertEquals(AmazonEC2, ec2)
        self.assertEquals('EC2_AP_SOUTHEAST2', ec2.PROVIDER_NAME)

        one = base.get_cloud('OPENNEBULA')
        self.assertEquals(OpenNebula, one)
        self.assertEquals('OPENNEBULA', one.PROVIDER_NAME)

class BaseCloudTest(unittest.TestCase):

    def setUp(self):
        base.CLOUDS_MAPPING['DUMMY'] = 'tests.DummyCloud'
        base.AVAILABLE_CLOUDS = {
            'tests.DummyCloud': { 'creds': '', }
        }
        self.Cloud = base.get_cloud('DUMMY')

    def test_test_conn(self):
        self.failUnless(self.Cloud.test_conn(creds=''))

    def test_init(self):
        cloud = self.Cloud()

        self.failUnless(cloud.ssh_private_key.endswith('id_rsa'))
        self.assertEquals(cloud.ssh_public_key, cloud.ssh_private_key + '.pub')

        self.assertEquals('root', cloud.login_as)

    def test_startup(self):
        cloud = self.Cloud()
        new_node = cloud.startup({})

        self.assertEquals(dict, type(new_node))
        self.assertEquals('RUNNING', new_node['state'])

    def test_is_running(self):
        cloud = self.Cloud()

        self.failUnless(cloud.is_running(node_id='1'))
        self.failIf(cloud.is_running(node_id='42'))

    def test_shutdown(self):
        cloud = self.Cloud()

        # node 42 is not running. shutdown should return False
        self.failIf(cloud.shutdown(node_id='42'))

        # this one does not work, libcloud's DUMMY driver is a bit outdated
        #self.failUnless(cloud.shutdown(node_id='1'))

    def test_reboot(self):
        cloud = self.Cloud()

        # node 42 is not running. reboot should return False
        self.failIf(cloud.reboot(node_id='42'))

        # node 1 is running. reboot should return True
        self.failUnless(cloud.reboot(node_id='1'))

    def test_list_nodes(self):
        nodes = self.Cloud().list_nodes()
        self.assertEquals(2, len(nodes))

        for node in nodes:
            self.assertEquals('RUNNING', node['state'])

    def test_list_images(self):
        images = self.Cloud().list_images()

        self.assertEquals(3, len(images))

        self.assertEquals('Ubuntu 9.10', images[0].name)
        self.assertEquals('Ubuntu 9.04', images[1].name)
        self.assertEquals('Slackware 4', images[2].name)

if __name__ == "__main__":
    unittest.main()
