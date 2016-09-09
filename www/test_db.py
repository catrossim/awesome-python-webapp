import uuid, time
def next_id(t=None):
    '''
    Return next id as 50-char string.
    Args:
        t: unix timestamp, default to None and using time.time().
    '''
    if t is None:
        t = time.time()
    return '%015d %s 000' % (int(t * 1000), uuid.uuid4().hex)

domain = uuid.uuid3(uuid.NAMESPACE_DNS,'crose.com')
post = uuid.uuid3(domain,'what-is-a-metaclass-in-python')
print uuid.NAMESPACE_DNS
print domain,post
