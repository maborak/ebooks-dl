import ssl
import urllib.request


def wget(url: str) -> str:
    """Request page URL

    Arguments:
        url {str} -- [description]

    Returns:
        str -- [description]
    """
    context = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; ' +
            'Intel Mac OS X 10_9_3) AppleWebKit/537.36' +
            ' (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req, context=context)
    return f.read()
