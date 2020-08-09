# PROXYUP

ProxyUP is a package designed for retrieving proxies from a public API. Transparently, it will only retrieve valid proxies, 
checking them constantly at a fixed rate and ensuring the proxies answer before their delivery.


## Installation

It can be installed through pip:

```python
pip install proxyup
```

## Basic Usage

As soon as the retriever is instantiated, it will scrap proxies in the background at a fixed rate. Internally it will hold a set of valid proxies that are periodically checked and updated. 


In order to get a list of 4 proxies, the `get_once` method can be used:
```python
from proxyup import ProxyupRetriever

with ProxyupRetriever(proxy_type="http") as proxies:   # Valid proxy types=["http", "socks4", "socks5"]
    proxies_list = proxies.get_once(4) 

print(proxies_list)

['http://X.X.X.X:XXXX', 'http://X.X.X.X:XXXX', 'http://X.X.X.X:X', 'http://X.X.X.X:X']
```

All the returned proxies have passed properly the control measures. These measures consists of the following rules:
  * They all had a server listening on the specified port.
  * They all answered with a 200 status code when requested https://www.google.com through them.
  * They all were responsive in the last `60` seconds. This parameter is modificable throguh the `check_interval_seconds` during instantiation of the class.


## Advanced usage

If desired, it can be wrapped in an infinite iterator that retrieves X number of proxies as follows:
```python
from proxyup import ProxyupRetriever

with ProxyupRetriever(proxy_type="http") as proxies:   # Valid proxy types=["http", "socks4", "socks5"]

    for proxies_list in proxies[4]:   # The index es the size of the list to retrieve in a single shot  
        print(proxies_list)

['http://X.X.X.X:XXXX', 'http://X.X.X.X:XXXX', 'http://X.X.X.X:X', 'http://X.X.X.X:X']
['http://X.X.X.X:XXXX', 'http://X.X.X.X:XXXX', 'http://X.X.X.X:X', 'http://X.X.X.X:X']
['http://X.X.X.X:XXXX', 'http://X.X.X.X:XXXX', 'http://X.X.X.X:X', 'http://X.X.X.X:X']
...
```

This iterator will run forever, reporting valid proxies on each iteration, which may be the same or different proxies than the previous iteration. 

If a valid proxy is detected to not be valid anymore, it will never be yielded again. 
The internal proxy list is constantly being updated at a rate of `120` seconds, a value that can be modified by using the `update_interval_seconds` parameter. 

A single update will scrap around 100-200 new proxies to include in the proxies list. Previous proxies are not removed unless they are detected to not be valid anymore.

In order to avoid an internal list overflow, a limit is specified in the number of internal max proxies allowed to be kept for checks. This value is by default 1000 proxies, but it can be modified throught the parameter `proxy_cache_size`.  
 
The proxies can also be handled outside of a context manager as follows:
```python
from proxyup import ProxyupRetriever

proxies = ProxyupRetriever()
proxies.start()

try:
    proxy = proxies.get_once()
finally:
    proxies.close()
```

Note that it is important to close the proxies object. Otherwise, their internal threads will not know when to finish and will run in background forever, avoiding the process termination.


# References
This package, as of version 0.0.1, uses the API from https://proxyscrape.com/ to scrap new proxies. Note that this backend might change in future releases of the package.