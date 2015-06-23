import datetime
from configparser import ConfigParser
from functools import wraps
from xmlrpc.client import ServerProxy

from pymongo import MongoClient

config = ConfigParser()
config.read('testopia.ini')

api = config['testopia']['api']
user = config['testopia']['user']
passwd = config['testopia']['passwd']

uri = api.replace('://', '://%s:%s@' % (user,passwd), 1)
proxy = ServerProxy(uri, use_datetime=True)

mongo_uri = config['mongodb']['uri']
mongo_client = MongoClient('mongodb://%s' % mongo_uri)
mongo_tt = mongo_client.tt.cases
mongo_bz = mongo_client.bz.prods

def double_find(func):
    '''this is a wrapper. if the func return None then re-execute again.'''
    @wraps(func)
    def double_func(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return result
        else:
            return func(*args, **kwargs)
    return double_func

@double_find
def get_id_by_email(email):
    result=mongo_tt.find_one({'name':'user', 'email':email})
    if result:
        return result.get('id'), result.get('real_name')
    
    #should get from bugzilla server side if no data found from mongodb
    user = proxy.User.get({'names':email})
    user = user.get('users')[0]
    if user:
        user = {k:user[k] for k in ('email', 'id', 'real_name')}
        user['name'] = 'user'
        mongo_tt.replace_one({'name':'user', 'email':email}, user, upsert=True)

