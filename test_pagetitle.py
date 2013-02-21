import unittest
from pagetitle import PageTitle

class TestPageTitle(unittest.TestCase):
    def testLoads(self):
        p = PageTitle({'pageTitle':None})
        t = p.getPageTitle("http://bigasterisk.com/")
        self.assertEqual(t, "Drew Perttula")
        
