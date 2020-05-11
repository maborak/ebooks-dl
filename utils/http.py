import ssl
import urllib.request
import time
import urllib3


def wget(url: str, referer: str = '') -> str:
    http = urllib3.PoolManager()
    headers = {
        'Referer': referer if referer else 'https://google.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    try:
        r = http.request('GET', url, headers=headers)
        print(r.status)
        return r.data
    except Exception as e:
        print("-------------- http-error BEGIN --------------")
        print(e)
        print("-------------- http-error ENG --------------")
        return ''
    


def wget2(url: str, referer: str = '') -> str:
    """Request page URL

    Arguments:
        url {str} -- [description]

    Returns:
        str -- [description]
    """
    time.sleep(2)
    context = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'Referer': referer if referer else 'https://google.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    try:
        f = urllib.request.urlopen(req, context=context)
        return f.read()
    except Exception as e:
        print(e)
        return ''
