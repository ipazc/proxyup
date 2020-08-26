import concurrent
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import time
import requests

from threading import Lock, Thread


MAX_EPSILON = 10**10


def log_debug(*args, **kwargs):
    pass#print(*args, **kwargs)


class ProxyupRetriever:
    URL = "https://api.proxyscrape.com/?request=getproxies&proxytype={}&timeout={}&country={}&ssl=all&anonymity=all"
    CHECK_URL = "https://www.google.com/"

    def __init__(self, proxy_type="http", proxy_country="all", proxy_timeout=500, pool_njobs=5, check_url=CHECK_URL,
                 update_interval_seconds=120, check_interval_seconds=60, auto_start=True, proxy_cache_size=1000):
        self._proxy_type = proxy_type
        self._pool_checker = ThreadPoolExecutor(pool_njobs, thread_name_prefix="proxyup")
        self._update_interval_seconds = update_interval_seconds
        self._check_interval_seconds = check_interval_seconds
        self._proxy_cache_size = proxy_cache_size
        self._proxy_timeout = proxy_timeout
        self._proxy_country = proxy_country
        self._check_url = check_url

        self._num_proxies_to_deliver_simultaneously = 1
        self._timeout_iteration_seconds = 0

        self._finish = False
        self._thread = None
        self._lock = Lock()
        self._proxies = pd.DataFrame([], columns=["Confirmed", "LastCheck"], index=pd.Index([], name="Address"))
        self._blacklist = []

        if auto_start:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        self.stop()

    @property
    def finish(self):
        with self._lock:
            result = self._finish
        return result

    @finish.setter
    def finish(self, value):
        with self._lock:
            self._finish = value

    def start(self):
        if self._thread is None:
            self.finish = False
            self._thread = Thread(target=self._retrieve, daemon=True)
            self._thread.start()
            log_debug("Start requested")

    def stop(self):
        if not self.finish and self._thread is not None:
            log_debug("Stop requested")
            self.finish = True

            self._pool_checker.shutdown(wait=False)
            self._thread.join()
            self._thread = None

    def __del__(self):
        self.stop()

    def _retrieve(self):
        log_debug("Started")

        seconds_from_last_check = 0
        futures = []

        while not self.finish:

            # Event handler for update proxies
            if seconds_from_last_check % self._update_interval_seconds == 0:
                self._event_update_proxies()

            # Event handler for check proxies
            if len(futures) == 0 and seconds_from_last_check % self._check_interval_seconds == 0:
                futures = self._event_check_proxies()

            done, working = concurrent.futures.wait(futures, timeout=0.01)
            futures = working

            seconds_from_last_check = (seconds_from_last_check + 1) % MAX_EPSILON
            time.sleep(1)

        log_debug("Finished")

    def _event_update_proxies(self):
        log_debug("Update event raised")
        proxy_list_df = pd.DataFrame([], index=pd.Index(self._get_proxies(), name="Address"))

        log_debug(f"Got {proxy_list_df.shape[0]} proxies to add")

        with self._lock:
            if self._proxies.shape[0] > self._proxy_cache_size:
                log_debug(f"Proxies list size limit reached. Not filling with new ones until it is required.")
                return

            are_first_proxies = self._proxies.shape[0] == 0
            self._proxies = pd.concat([self._proxies, proxy_list_df], axis=1)
            self._proxies["LastCheck"] = pd.to_datetime(self._proxies["LastCheck"])
            log_debug(f"Proxies list updated to {self._proxies.shape[0]}")

        if are_first_proxies:
            self._event_check_proxies()

    def _event_check_proxies(self):
        log_debug("Check event raised")

        with self._lock:
            # 1. We get the list of proxies that must be checked
            proxies_to_check = self._proxies[
                ((datetime.now() - self._proxies['LastCheck']).dt.total_seconds() > self._check_interval_seconds)
                | (self._proxies['LastCheck'].isna())
            ].index

        log_debug(f"Got {proxies_to_check.shape[0]} proxies to check")

        # 2. We send to the pool the update on them
        futures = [self._pool_checker.submit(self._check_proxy, proxy) for proxy in proxies_to_check]

        log_debug("Check event finished")
        return futures

    def _check_proxy(self, proxy):
        if self.finish:
            return

        log_debug(f"Checking {proxy}")
        proxy_dict = {
            "http": proxy,
            "https": proxy
        }

        try:
            response = requests.get(self._check_url, proxies=proxy_dict, timeout=3)
            status_code = response.status_code

        except requests.exceptions.ProxyError:
            status_code = 500

        if status_code == 200:
            # We found a valid proxy
            with self._lock:
                self._proxies.loc[proxy, ["Confirmed", "LastCheck"]] = [True, datetime.now()]
                log_debug(f"Proxy {proxy} valid")
        else:
            # Proxy is no longer valid (if it ever was)
            with self._lock:
                self._proxies.drop(proxy, axis=0)
                log_debug(f"Proxy {proxy} not valid. Removed")

    def get_once(self, number=1, timeout=0):
        if self._thread is None:
            raise Exception("Proxy scan thread is not started. Use Start() method or wrap the instance with a context"
                            " manager before attempting to get proxies.")

        for proxy in self[number:timeout]:
            return proxy

    def blacklist(self, proxy):
        """
        Blacklists a given proxy. This proxy will never be returned again.
        :param proxy: proxy to blacklist, in the format 'protocol://IP:PORT'
        """
        with self._lock:
            self._blacklist = list(self._blacklist)
            self._blacklist.append(proxy)
            self._blacklist = set(self._blacklist)

    def _get_proxies(self):
        proxies = requests.get(self.URL.format(self._proxy_type, self._proxy_timeout, self._proxy_country)).text
        proxies = [f"{self._proxy_type}://{p}" for p in proxies.split("\r\n") if p != ""]
        return proxies

    def __getitem__(self, return_config):
        if self._thread is None:
            raise Exception("Proxy scan thread is not started. Use Start() method or wrap the instance with a context"
                            " manager before attempting to get proxies.")

        if type(return_config) is int:
            self._num_proxies_to_deliver_simultaneously = return_config

        elif type(return_config) is slice:
            self._num_proxies_to_deliver_simultaneously = return_config.start
            self._timeout_iteration_seconds = return_config.stop

        return self

    def __iter__(self):
        if self._thread is None:
            raise Exception("Proxy scan thread is not started. Use Start() method or wrap the instance with a context"
                            " manager before attempting to get proxies.")

        seconds_spent = 0

        while True:
            seconds_spent = (seconds_spent + 1) % MAX_EPSILON

            if self._timeout_iteration_seconds > 0 and seconds_spent % self._timeout_iteration_seconds == 0:
                break

            with self._lock:
                valid_proxies = self._proxies[self._proxies['Confirmed'] == True]
                valid_proxies = valid_proxies.loc[[proxy for proxy in valid_proxies.index if proxy not in self._blacklist]]

            if valid_proxies.shape[0] >= self._num_proxies_to_deliver_simultaneously:
                valid_proxy = valid_proxies.sample(self._num_proxies_to_deliver_simultaneously).index.tolist()

                if self._num_proxies_to_deliver_simultaneously == 1:
                    valid_proxy = valid_proxy[0]

                yield valid_proxy

            time.sleep(1)
