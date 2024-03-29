import json
import logging
from collections.abc import Hashable, Iterable
from copy import deepcopy
from urllib.parse import quote as urlquote

from sseclient import SSEClient


class DB ():
    """ 
    A class for interacting with a specific OrbitDB database.
    """
    def __init__(self, client, params, **kwargs):
        """
        Initialize a DB object.
        Args:
            client (OrbitDbAPI): The client object used to interact with the API.
            params (dict): A dictionary of parameters for the database.
            **kwargs: Additional keyword arguments.
            - 'use_db_cache': Whether to use a cache for database objects (bool, default=True).
            - 'enforce_caps': Whether to enforce the presence of capabilities in the database (bool, default=True).
            - 'enforce_indexby': Whether to enforce the presence of an indexBy option in the database (bool, default=True).
        """
        self.__cache = {}
        self.__client = client
        self.__params = params
        self.__db_options = params.get('options', {})
        self.__dbname = params['dbname']
        self.__id = params['id']
        self.__id_safe = urlquote(self.__id, safe='')
        self.__type = params['type']
        self.__use_cache = kwargs.get('use_db_cache', client.use_db_cache)
        self.__enforce_caps = kwargs.get('enforce_caps', True)
        self.__enforce_indexby = kwargs.get('enforce_indexby', True)

        self.logger = logging.getLogger(__name__)
        self.__index_by = self.__db_options.get('indexBy')


    def clear_cache(self):
        """
        Clear the cache of the database.
        """
        self.__cache = {}

    def cache_get(self, item):
        """
        Retrieve an item from the cache of the database.
        Args:
        item: The item to retrieve from the cache.
        """
        item = str(item)
        return deepcopy(self.__cache.get(item))

    def cache_remove(self, item):
        """
        Remove an item from the cache of the database.
        Args:
        item: The item to remove from the cache.
        """
        item = str(item)
        if item in self.__cache:
            del self.__cache[item]

    @property
    def cached(self):
        """
        Returns whether the client uses a cache for database objects.
        """
        return self.__use_cache

    @property
    def index_by(self):
        """
        Returns the indexBy option of the database.
        """
        return self.__index_by

    @property
    def cache(self):
        """
        Returns the cache of the database.
        """
        return deepcopy(self.__cache)

    @property
    def params(self):
        """
        Returns the parameters of the database.
        """
        return deepcopy(self.__params)

    @property
    def dbname(self):
        """
        Returns the name of the database.
        """
        return self.__dbname

    @property
    def id(self):
        """
        Returns the id of the database.
        """
        return self.__id

    @property
    def dbtype(self):
        """
        Returns the type of the database.
        """
        return self.__type

    @property
    def capabilities(self):
        """
        Returns the capabilities of the database.
        """
        return deepcopy(self.__params.get('capabilities', []))

    @property
    def queryable(self):
        """
        Returns whether the database is queryable.
        """
        return 'query' in self.__params.get('capabilities', [])

    @property
    def putable(self):
        """
        Returns whether the database is putable.
        """
        return 'put' in self.__params.get('capabilities', [])

    @property
    def removeable(self):
        """
        Returns whether the database is removeable.
        """
        return 'remove' in self.__params.get('capabilities', [])

    @property
    def iterable(self):
        """
        Returns whether the database is iterable.
        """
        return 'iterator' in self.__params.get('capabilities', [])

    @property
    def addable(self):
        """
        Returns whether the database is addable.
        """
        return 'add' in self.__params.get('capabilities', [])

    @property
    def valuable(self):
        """
        Returns whether the database is valuable.
        """
        return 'value' in self.__params.get('capabilities', [])

    @property
    def incrementable(self):
        return 'inc' in self.__params.get('capabilities', [])

    @property
    def indexed(self):
        return 'indexBy' in self.__db_options

    @property
    def can_append(self):
        return self.__params.get('canAppend')

    @property
    def write_access(self):
        return deepcopy(self.__params.get('write'))

    def info(self):
        endpoint = '/'.join(['db', self.__id_safe])
        return self.__client._call('GET', endpoint)

    def get(self, item, cache=None, unpack=False):
        if cache is None: cache = self.__use_cache
        item = str(item)
        if cache and item in self.__cache:
            result = self.__cache[item]
        else:
            endpoint = '/'.join(['db', self.__id_safe, item])
            result = self.__client._call('GET', endpoint)
            if cache: self.__cache[item] = result
        if isinstance(result, Hashable): return deepcopy(result)
        if isinstance(result, Iterable): return deepcopy(result)
        if unpack:
            if isinstance(result, Iterable): return deepcopy(next(result, {}))
            if isinstance(result, list): return deepcopy(next(iter(result), {}))
        return result

    def get_raw(self, item):
        endpoint = '/'.join(['db', self.__id_safe, 'raw', str(item)])
        return (self.__client._call('GET', endpoint))

    def put(self,  item, cache=None):
        if self.__enforce_caps and not self.putable:
            raise CapabilityError(f'Db {self.__dbname} does not have put capability')
        if self.indexed and (not self.__index_by in item) and self.__enforce_indexby:
            raise MissingIndexError(f"The provided document {item} doesn't contain field '{self.__index_by}'")

        if cache is None: cache = self.__use_cache
        if cache:
            if self.indexed and hasattr(item, self.__index_by):
                    index_val = getattr(item, self.__index_by)
            else:
                index_val = item.get('key')
            if index_val:
                self.__cache[index_val] = item
        endpoint = '/'.join(['db', self.__id_safe, 'put'])
        entry_hash = self.__client._call('POST', endpoint, json=item).get('hash')
        if cache and entry_hash: self.__cache[entry_hash] = item
        return entry_hash

    def add(self, item, cache=None):
        if self.__enforce_caps and not self.addable:
            raise CapabilityError(f'Db {self.__dbname} does not have add capability')
        if cache is None: cache = self.__use_cache
        endpoint = '/'.join(['db', self.__id_safe, 'add'])
        entry_hash = self.__client._call('POST', endpoint, json=item).get('hash')
        if cache and entry_hash: self.__cache[entry_hash] = item
        return entry_hash

    def inc(self, val):
        val = int(val)
        endpoint = '/'.join(['db', self.__id_safe, 'inc'])
        return self.__client._call('POST', endpoint, json={'val':val})

    def value(self):
        endpoint = '/'.join(['db', self.__id_safe, 'value'])
        return self.__client._call('GET', endpoint)

    def iterator_raw(self, **kwargs):
        if self.__enforce_caps and not self.iterable:
            raise CapabilityError(f'Db {self.__dbname} does not have iterator capability')
        endpoint =  '/'.join(['db', self.__id_safe, 'rawiterator'])
        return self.__client._call('GET', endpoint, json=kwargs)

    def iterator(self, **kwargs):
        if self.__enforce_caps and not self.iterable:
            raise CapabilityError(f'Db {self.__dbname} does not have iterator capability')
        endpoint =  '/'.join(['db', self.__id_safe, 'iterator'])
        return self.__client._call('GET', endpoint, json=kwargs)

    def index(self):
        endpoint = '/'.join(['db', self.__id_safe, 'index'])
        result = self.__client._call('GET', endpoint)
        return result

    def all(self):
        endpoint = '/'.join(['db', self.__id_safe, 'all'])
        result = self.__client._call('GET', endpoint)
        if isinstance(result, Hashable):
            self.__cache = result
        return result

    def remove(self, item):
        if self.__enforce_caps and not self.removeable:
            raise CapabilityError(f'Db {self.__dbname} does not have remove capability')
        item = str(item)
        endpoint = '/'.join(['db', self.__id_safe, item])
        return self.__client._call('DELETE', endpoint)

    def unload(self):
        endpoint = '/'.join(['db', self.__id_safe])
        return self.__client._call('DELETE', endpoint)

    def events(self, eventname):
        endpoint = '/'.join(['db', self.__id_safe, 'events', urlquote(eventname, safe='')])
        res = self.__client._call_raw('GET', endpoint, stream=True)
        res.raise_for_status()
        return SSEClient(res.stream()).events()

    def findPeers(self, **kwargs):
        endpoint = '/'.join(['peers','searches','db', self.__id_safe])
        return self.__client._call('POST', endpoint, json=kwargs)

    def getPeers(self):
        endpoint = '/'.join(['db', self.__id_safe, 'peers'])
        return self.__client._call('GET', endpoint)


class CapabilityError(Exception):
    pass

class MissingIndexError(Exception):
    pass
