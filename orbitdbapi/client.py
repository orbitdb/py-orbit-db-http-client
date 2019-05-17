import json
import logging
import requests
from .db import DB
from hyper.contrib import HTTP20Adapter
from urllib.parse import quote as urlquote

class OrbitDbAPI ():
    def __init__ (self, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.__config = kwargs
        self.__base_url = self.__config.get('base_url')
        self.__use_db_cache = self.__config.get('use_db_cache', True)

        self.__session = requests.Session()
        self.__session.mount(self.__base_url, HTTP20Adapter(timeout=self.__config.get('timeout', 30)))

    @property
    def use_db_cache(self):
        return self.__use_db_cache

    def _do_request(self, *args, **kwargs):
        try:
            return self.__session.request(*args, **kwargs)
        except:
            self.logger.exception('Exception during api call')
            raise

    def _call(self, method, endpoint, body=None):
        url = '/'.join([self.__base_url, endpoint])
        res = self._do_request(method, url, json=body)
        try:
            result = res.json()
        except:
            self.logger.warning('Json decode error', exc_info=True)
            self.logger.debug(res.text)
            raise
        try:
            res.raise_for_status()
        except:
            self.logger.exception('Server Error')
            self.logger.debug(result)
            raise
        return result

    def list_dbs(self):
        return self._call('get', 'dbs')

    def db(self, dbname, **kwargs):
        return DB(self, self.open_db(dbname, **kwargs), **self.__config)

    def open_db(self, dbname, **kwargs):
        endpoint = '/'.join(['db', urlquote(dbname, safe='')])
        return self._call('post', endpoint, kwargs)
