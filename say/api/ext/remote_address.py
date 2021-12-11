from flask import request


CLOUDFLARE_IP_HEADER_KEY = 'Cf-Connecting-Ip'


def get_remote_address():

    """
    :return: the ip address for the current request
     (or 127.0.0.1 if none found)

    """
    return (
        request.headers.get(CLOUDFLARE_IP_HEADER_KEY)
        or request.remote_addr
        or '127.0.0.1'
    )
