from website import app, database
from flask import request

import MySQLdb
import Queue

pool = database.pool

@app.route('/itemFound', methods=['POST'])
def itemFound():
    try:
        connection = pool.get()
    except MySQLdb.OperationalError, e:
        app.logger.error(e)
        return ''

    try:
        cursor = connection.cursor()
        cursor.execute('insert into item_found values (NULL, INET_ATON(%s), NULL, %s, %s, %s, %s, %s)',
                       (request.remote_addr, request.form['steamid'], request.form['method'],
                        request.form['quality'], request.form['item'], request.form['propername'] == '1'))
        connection.commit()
    except MySQLdb.OperationalError, e:
        app.logger.error(e)
    finally:
        cursor.close()
        pool.put(connection)
    return ''
