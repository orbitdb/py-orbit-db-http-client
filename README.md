# py-orbit-db-http-client

[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/orbitdb/Lobby) [![Matrix](https://img.shields.io/badge/matrix-%23orbitdb%3Apermaweb.io-blue.svg)](https://riot.permaweb.io/#/room/#orbitdb:permaweb.io)

> A python client for the Orbitdb HTTP API

Status: Proof-of-concept

------------------------------
## Install

### Install from `pip`
```sh
pip install orbitdbapi
```

### Install using source
Clone, and then run:
```sh
py setup.py
```
-----------------------------
## Usage
> 
```
from orbitdbapi import OrbitDbAPI
client = OrbitDbAPI(base_url='http://localhost:3000')
```
You can then use the client object to list all the databases available on the API:
```
dbs = client.list_dbs()
print(dbs)
```
To open a specific database, you can use the db() method, providing the name of the database as an argument:
```
db = client.db('mydb')
```
Once you have a DB object, you can use it to perform CRUD operations on the database. For example, to add an entry to the database:
```
db.add({'key': 'value'})
```
To retrieve all the entries in the database:
```
entries = db.all()
print(entries)
```
To retrieve a specific entry by its key:
```
entry = db.get('key')
print(entry)
```
To update an entry:
```
db.update('key', {'key': 'new_value'})
```
To remove an entry:
```
db.remove('key')
```

check the Jupyter Notebook example for local testing : [orbitdb_test.ipynb](./example/orbitdb_test.ipynb)

-----------------------

## Contributing

This is a work-in-progress. Feel free to contribute by opening issues or pull requests.

--------------------------

## License

[MIT Copyright (c) 2019 phillmac](LICENSE)
