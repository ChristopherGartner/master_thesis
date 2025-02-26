import random
import string
import time

from flask import request
from loguru import logger


class Toolbox:

    def createHash(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    """
    Logs a request's metadata into the 'hits' database table.

    Extracts the client's IP address (considering proxy headers), request URI, and various HTTP headers from the 
    provided request object, then inserts this data along with a timestamp into the 'hits' table. The IP address 
    is determined either from 'REMOTE_ADDR' or 'HTTP_X_FORWARDED_FOR' if the request is proxied. Additional 
    request details like user agent, accept language, path, and query string are also recorded. Logs the IP and 
    URI to the application logger for debugging purposes.

    Args:
        req: The Flask request object containing environment variables with request metadata.
        db: A database connection object with an execute method for running SQL queries.

    Returns:
        str: The IP address of the client making the request.

    Note:
        If 'REQUEST_URI' is not present in the request environment, an empty string is used as a fallback.
    """
    def logToDatabase(self, req, db):
        ip = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = (request.environ['REMOTE_ADDR'])
        else:
            ip = (request.environ['HTTP_X_FORWARDED_FOR'])  # if behind a proxy
        uri = req.environ.get('REQUEST_URI')
        if uri is None:
            uri = ""
        logger.info(ip + " " + uri)
        db.execute("INSERT INTO hits(ip, timestamp, url, sec_ch_ua, sec_ch_ua_mobile, sec_ch_ua_platform, "
                        "user_agent, accept_language, path, query) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (ip, int(time.time()), uri, req.environ.get('HTTP_SEC_CH_UA'),
                         req.environ.get('HTTP_SEC_CH_UA_MOBILE'), req.environ.get('HTTP_SEC_CH_UA_PLATFORM'),
                         req.environ.get('HTTP_USER_AGENT'), req.environ.get('HTTP_ACCEPT_LANGUAGE'),
                         req.environ.get('PATH_INFO'), req.environ.get('QUERY_STRING')), commit=True)
        return ip

    def isMobile(self, request, isMobile = False):
        ua = request.headers.get('User-Agent')
        if ua is None:
            ua = ""
        ua = ua.lower()
        if isMobile:
            ua += "android"
        return "iphone" in ua or "android" in ua