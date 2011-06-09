from config import config

import MySQLdb
import Queue

database = config['application']['database']

# Super simple connection pooling
class ConnectionPool(object):
    def __init__(self):
        self._pool = Queue.Queue()

    def _newConnection(self):
        return MySQLdb.connect(host=database['instance']['hostname'],
                               user=database['instance']['users']['writeonly']['username'],
                               passwd=database['instance']['users']['writeonly']['password'],
                               db=database['instance']['database'])

    def get(self):
        try:
            connection = self._pool.get(block=False)
        except Queue.Empty:
            connection = self._newConnection()
        return connection

    def put(self, connection):
        self._pool.put(connection)

pool = ConnectionPool()
