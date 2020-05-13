import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random
from pprint import pprint as pp

s = requests.Session()
retries = Retry(total=15,
                backoff_factor=random.randint(1, 5),
                status_forcelist=[500, 502, 503, 504])

s.mount('https://', HTTPAdapter(max_retries=retries))
s.mount('http://', HTTPAdapter(max_retries=retries))


def wget(url: str, referer: str = '') -> str:
    headers = {
        'Referer': referer if referer else 'https://google.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    data = s.get(url, headers=headers)
    # pp(data.request.headers)
    # exit()
    if data.status_code != 200:
        print(f"||||||||||||||||||||||||||||| {url} : {data.status_code}")
    return data.content
