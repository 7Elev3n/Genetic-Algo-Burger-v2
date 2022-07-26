import GenEvol  # Code to be tested
import unittest # Testing framework

class Test_evol(unittest.TestCase):
    def test_repeatability(self):
        self.assertEqual(GenEvol.evol(True))

