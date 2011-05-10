from website import app, config
from flask import request

import MySQLdb
import Queue
import yaml

database = config['application']['database']

# Super simple connection pooling
class ConnectionPool(object):
    def __init__(self):
        self._pool = Queue.Queue()

    def _newConnection(self):
        MySQLdb.connect(host=database['instance']['hostname'],
                        user=database['instance']['users']['writeonly']['username'],
                        passwd=database['instance']['users']['writeonly']['password'],
                        db=database['instance']['database'])

    def get(self):
        try:
            connection = connection_pool.get(block=False)
        except Queue.Empty:
            try:
                connection = self._newConnection()
            except Exception, e:
                app.logger.error(e)
                raise Exception('Cannot connect to database.')
        return connection

    def put(self, connection):
        self._pool.put(connection)

pool = ConnectionPool()

@app.route('/itemFound', methods=['POST'])
def itemFound():
    try:
        connection = pool.get()
    except:
        return ''

    try:
        cursor = connection.cursor()
        cursor.execute('insert into item_found values (NULL, INET_ATON(%s), NULL, %s, %s, %s, %s, %s)',
                       (request.remote_addr, request.form['steamid'], request.form['method'],
                        request.form['quality'], request.form['item'], request.form['propername'] == '1'))
        connection.commit()
    except Exception, e:
        app.logger.error(e)
    finally:
        cursor.close()
        pool.put(connection)
    return ''
