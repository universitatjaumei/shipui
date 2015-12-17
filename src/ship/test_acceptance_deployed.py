import urllib2, unittest

def deploy(warfile):
    pass

class TestAcceptanceWebApplicationDeployed(unittest.TestCase):

    def setUp(self):
        pass

    def test_deployed(self):
        deploy("sample.war")

        response = urllib2.urlopen('http://localhost:8888/sample/index.jsp')
        html = response.read()

        self.assertTrue(html.count("Hello!") > 0)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
