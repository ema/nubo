# -*- coding: utf-8 -*-

from nubo.clouds import base

from nubo.clouds.ec2 import AmazonEC2
from nubo.clouds.opennebula import OpenNebula

import unittest
import tempfile

from os import getenv, unlink
from os.path import join

class DummyCloud(base.BaseCloud):
    """Dummy cloud using the DUMMY libcloud provider"""
    PROVIDER_NAME = 'DUMMY'

    def wait_for_ssh(self, node):
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

        # Write dummy private key file
        self.privkey = tempfile.mkstemp()[1]

        # Write dummy public key file
        self.pubkey = self.privkey + '.pub'
        open(self.pubkey, 'w').write('')

        self.CloudClass = base.get_cloud('DUMMY')
        self.cloud = self.CloudClass(ssh_private_key=self.privkey)

    def tearDown(self):
        unlink(self.privkey)
        unlink(self.pubkey)

    def test_test_conn(self):
        self.failUnless(self.CloudClass.test_conn(creds=''))

    def test_init(self):
        self.assertEquals(self.cloud.ssh_public_key, 
            self.cloud.ssh_private_key + '.pub')

        self.assertEquals('root', self.cloud.login_as)

    def test_startup(self):
        new_node = self.cloud.startup({})

        self.assertEquals(dict, type(new_node))
        self.assertEquals('RUNNING', new_node['state'])

    def test_is_running(self):
        self.failUnless(self.cloud.is_running(node_id='1'))
        self.failIf(self.cloud.is_running(node_id='42'))

    def test_shutdown(self):
        # node 42 is not running. shutdown should return False
        self.failIf(self.cloud.shutdown(node_id='42'))

        # this one does not work, libcloud's DUMMY driver is a bit outdated
        #self.failUnless(cloud.shutdown(node_id='1'))

    def test_reboot(self):
        # node 42 is not running. reboot should return False
        self.failIf(self.cloud.reboot(node_id='42'))

        # node 1 is running. reboot should return True
        self.failUnless(self.cloud.reboot(node_id='1'))

    def test_list_nodes(self):
        nodes = self.cloud.list_nodes()
        self.assertEquals(2, len(nodes))

        for node in nodes:
            self.assertEquals('RUNNING', node['state'])

    def test_list_images(self):
        images = self.cloud.list_images()

        self.assertEquals(3, len(images))

        self.assertEquals('Ubuntu 9.10', images[0].name)
        self.assertEquals('Ubuntu 9.04', images[1].name)
        self.assertEquals('Slackware 4', images[2].name)

if __name__ == "__main__":
    unittest.main()
