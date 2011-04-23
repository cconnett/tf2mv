from website import app
from flask import request

import MySQLdb
import Queue

# Super simple connection pooling
mysqls = Queue.Queue()
for i in range(1):
    try:
        mysqls.put(MySQLdb.connect(host='mysql.tf2mv.com', user='item_found', passwd='redbull', db='tf2mv'))
    except:
        pass
        raise

@app.route('/itemFound', methods=['POST'])
def itemFound():
    try:
        mysql = mysqls.get(block=False)
    except Queue.Empty:
        app.logger.error('Not enough mysql connections.')
        return ''
    try:
        cursor = mysql.cursor()
        cursor.execute('insert into item_found values (NULL, INET_ATON(%s), NULL, %s, %s, %s, %s, %s)',
                       (request.remote_addr, request.form['steamid'], request.form['method'],
                        request.form['quality'], request.form['item'], request.form['propername'] == '1'))
        mysql.commit()
    except Exception as e:
        app.logger.error(e)
    finally:
        cursor.close()
        mysqls.put(mysql)
    return ''
