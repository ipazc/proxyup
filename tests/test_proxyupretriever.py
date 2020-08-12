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

    def test_retrieve_one_socks4(self):
        """
        ProxyRetriever gets a single proxy socks4 successfully
        :return:
        """
        with ProxyupRetriever(proxy_type="socks4") as proxies:
            proxy = proxies.get_once()

        self.assertTrue(len(proxy) > 0)
        self.assertTrue(proxy.startswith("socks4"))

        proxies = ProxyupRetriever(proxy_type="socks4")
        proxies.start()
        try:
            proxy = proxies.get_once()
        finally:
            proxies.close()

        self.assertTrue(len(proxy) > 0)
        self.assertTrue(proxy.startswith("socks4"))

    def test_retrieve_N_socks4(self):
        """
        ProxyRetriever gets a list of N proxies socks4 successfully
        :return:
        """
        with ProxyupRetriever(proxy_type="socks4") as proxies:
            proxy_list = proxies.get_once(PROXY_COUNT)

        self.assertTrue(len(proxy_list) == PROXY_COUNT)
        self.assertTrue(all([proxy.startswith("socks4") for proxy in proxy_list]))

        proxies = ProxyupRetriever(proxy_type="socks4")
        proxies.start()
        try:
            proxy = proxies.get_once(PROXY_COUNT)
        finally:
            proxies.close()

        self.assertTrue(len(proxy) == PROXY_COUNT)
        self.assertTrue(all([proxy.startswith("socks4") for proxy in proxy_list]))


if __name__ == '__main__':
    unittest.main()
