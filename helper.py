import redis


def redis_con():
    r = redis.Redis(
    host='192.168.99.100',
    port=32768,
    password='')
    return r


def redis_exid_exist(extid):
    r = redis_con()
    val = r.get(extid)
    return val


def redis_exid_register(extid, task_id):
    r = redis_con()
    r.set(extid, task_id)
    return



