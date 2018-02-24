import os
import redis


def cache(user):
    r = redis.from_url(os.environ.get("REDIS_URL"))
    if not r.get(user):
        r.set(user, False, ex=300)
        return False
    return r.ttl(user)

