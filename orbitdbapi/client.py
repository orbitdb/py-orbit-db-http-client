import json
import logging
from pprint import pformat
from urllib.parse import quote as urlquote

import httpx

from .db import DB


class OrbitDbAPI ():
    """
    A client for interacting with the OrbitDB HTTP API.
    """
    def __init__ (self, **kwargs):
        """
        Initialize the client with the provided configuration options.
        
        Args:
            kwargs (dict): A dictionary of configuration options.
                - 'base_url': The base URL of the OrbitDB API (str).
                - 'use_db_cache': Whether to use a cache for database objects (bool, default=True).
                - 'timeout': Timeout for API requests (int, default=30).
        Example:
            client = OrbitDbAPI(base_url='http://localhost:3000', use_db_cache=True, timeout=30)
        """
        self.logger = logging.getLogger(__name__)
        self.__config = kwargs
        self.__base_url = self.__config.get('base_url')
        self.__use_db_cache = self.__config.get('use_db_cache', True)
        self.__timeout = self.__config.get('timeout', 30)
        self.__session = httpx.Client()
        self.logger.debug('Base url: ' + self.__base_url)

    @property
    def session(self):
        """
        Returns the underlying HTTP session used by the client.
        """
        return self.__session

    @property
    def base_url(self):
        """
        Returns the base URL of the OrbitDB API.
        """
        return self.__base_url

    @property
    def use_db_cache(self):
        """
        Returns whether the client uses a cache for database objects.
        """
        return self.__use_db_cache

    def _do_request(self, *args, **kwargs):
        """
        Perform a raw request to the OrbitDB API.
        Args:
            *args: Positional arguments to pass to the session's request() method.
            **kwargs: Keyword arguments to pass to the session's request() method.
        """
        self.logger.log(15, json.dumps([args, kwargs]))
        kwargs['timeout'] = kwargs.get('timeout', self.__timeout)
        try:
            return self.__session.request(*args, **kwargs)
        except:
            self.logger.exception('Exception during api call')
            raise

    def _call_raw(self, method, endpoint, **kwargs):
        """
        Perform a raw API call and return the raw response.
        Args:
            method (str): HTTP method to use.
            endpoint (str): Endpoint to call.
            **kwargs: Additional keyword arguments to pass to the request.
        """
        url = '/'.join([self.__base_url, endpoint])
        return self._do_request(method, url, **kwargs)

    def _call(self, method, endpoint,  **kwargs):
        """
        Perform an API call and return the parsed JSON response.
        Args:
            method (str): HTTP method to use.
            endpoint (str): Endpoint to call.
            **kwargs: Additional keyword arguments to pass to the request.
        """
        res = self._call_raw(method, endpoint, **kwargs)
        try:
            result = res.json()
        except:
            self.logger.warning('Json decode error', exc_info=True)
            self.logger.log(15, res.text)
            raise
        try:
            res.raise_for_status()
        except:
            self.logger.exception('Server Error')
            self.logger.error(pformat(result))
            raise
        return result

    def list_dbs(self):
        """
        Retrieve a list of all databases on the OrbitDB API.
        """
        return self._call('GET', 'dbs')

    def db(self, dbname, local_options=None, **kwargs):
        """
        Open a database by name and return a DB object.
        Args:
            dbname (str): The name of the database to open.
            local_options (dict): A dictionary of options to pass to the DB object.
            **kwargs: Additional keyword arguments to pass to the open_db() method.
        Example:
            client = OrbitDbAPI()
            mydb = client.db("mydbname")
        """
        if local_options is None: local_options = {}
        return DB(self, self.open_db(dbname, **kwargs), **{**self.__config, **local_options})

    def open_db(self, dbname, **kwargs):
        """
        Open a database by name and return the raw JSON response.
        Args:
            dbname (str): The name of the database to open.
            **kwargs: Additional keyword arguments to pass to the request.
        """
        endpoint = '/'.join(['db', urlquote(dbname, safe='')])
        return self._call('POST', endpoint, **kwargs)

    def searches(self):
        """
        Retrieve a list of all searches on the OrbitDB API.
        """
        endpoint = '/'.join(['peers', 'searches'])
        return self._call('GET', endpoint)
