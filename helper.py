import redis


def redis_con():
    r = redis.Redis(
    host='192.168.99.100',
    port=32769,
    password='')
    return r


def redis_extid_exist(extid):
    r = redis_con()
    val = r.exists(extid)
    return val


def redis_get_guid(extid):
    r = redis_con()
    val = r.get(extid)
    return val


def redis_extid_register(extid, task_id):
    r = redis_con()
    r.set(extid, task_id)
    return
