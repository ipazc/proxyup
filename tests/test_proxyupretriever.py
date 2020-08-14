import unittest
from proxyup import ProxyupRetriever

PROXY_COUNT = 2


class TestProxyUPRetriever(unittest.TestCase):

    def test_retrieve_one_http(self):
        """
        ProxyRetriever gets a single proxy http successfully
        :return:
        """
        with ProxyupRetriever() as proxies:
            proxy = proxies.get_once()

        self.assertTrue(len(proxy) > 0)
        self.assertTrue(proxy.startswith("http"))


        proxies = ProxyupRetriever()
        proxies.start()
        try:
            proxy = proxies.get_once()
        finally:
            proxies.close()


        self.assertTrue(len(proxy) > 0)
        self.assertTrue(proxy.startswith("http"))

    def test_retrieve_N_http(self):
        """
        ProxyRetriever gets a list of N proxies http successfully
        :return:
        """
        with ProxyupRetriever() as proxies:
            proxy_list = proxies.get_once(PROXY_COUNT)

        self.assertTrue(len(proxy_list) == PROXY_COUNT)
        self.assertTrue(all([proxy.startswith("http") for proxy in proxy_list]))

        proxies = ProxyupRetriever()
        proxies.start()
        try:
            proxy = proxies.get_once(PROXY_COUNT)
        finally:
            proxies.close()

        self.assertTrue(len(proxy) == PROXY_COUNT)
        self.assertTrue(all([proxy.startswith("http") for proxy in proxy_list]))


if __name__ == '__main__':
    unittest.main()
