import unittest
from numpy.random import seed
from numpy.random import randn
from numpy.random import lognormal
import numpy as np

from statistic import ks_test_same_dist
ALPHA = 0.05


class TestStatistic(unittest.TestCase):

    def test_ks(self):
        seed(0x12345)
        data1 = randn(100)
        data2 = lognormal(3, 1, 100)
        x = np.random.normal(0, 1, 1000)
        y = np.random.normal(0, 1, 1000)
        z = np.random.normal(1.1, 0.9, 1000)
        test_same = ks_test_same_dist(x, y, ALPHA, True)
        self.assertTrue(test_same)
        test_diff = ks_test_same_dist(x, z, ALPHA, True)
        self.assertFalse(test_diff)
