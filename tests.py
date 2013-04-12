# -*- coding: utf-8 -*-

from nubo.clouds.base import get_cloud, supported_clouds

from nubo.clouds.ec2 import AmazonEC2
from nubo.clouds.opennebula import OpenNebula

import unittest

class BaseTest(unittest.TestCase):

    def test_supported_clouds(self):
        self.failUnless(supported_clouds())

        for cloud in supported_clouds():
            self.assertEquals(str, type(cloud))

    def test_get_cloud(self):
        ec2 = get_cloud('EC2_AP_SOUTHEAST2')
        self.assertEquals(AmazonEC2, ec2)
        self.assertEquals('EC2_AP_SOUTHEAST2', ec2.PROVIDER_NAME)

        one = get_cloud('OPENNEBULA')
        self.assertEquals(OpenNebula, one)
        self.assertEquals('OPENNEBULA', one.PROVIDER_NAME)

if __name__ == "__main__":
    unittest.main()
