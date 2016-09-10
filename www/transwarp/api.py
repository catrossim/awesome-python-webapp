# coding: utf-8
import json, functools
from web import ctx
class APIError(Exception):
    pass

def api(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        try:
            result = json.dumps(func(*args, **kw))
        except APIError, e:
            result = json.dumps(error=e.error, data=e.data, message=e.message)
        except Exception, e:
            result = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=e.message))
        ctx.response.content_type = 'application/json'
        return result
    return _wrapper
