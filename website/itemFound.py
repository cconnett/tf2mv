from website import app, config
from flask import request

import MySQLdb
import Queue
import yaml

database = config['application']['database']

# Super simple connection pooling
connection_pool = Queue.Queue()
for i in range(config['application']['database']['poolsize']):
    try:
        connection_pool.put(MySQLdb.connect(host=database['instance']['hostname'],
                                            user=database['instance']['users']['writeonly']['username'],
                                            passwd=database['instance']['users']['writeonly']['password'],
                                            db=database['instance']['database']))
    except Exception, e:
        app.logger.error(e)

@app.route('/itemFound', methods=['POST'])
def itemFound():
    try:
        connection = connection_pool.get(block=False)
    except Queue.Empty:
        app.logger.error('Not enough database connections.')
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
        connection_pool.put(connection)
    return ''
