from website import app

import MySQLdb
import Queue

# Super simple connection pooling
mysqls = Queue.Queue()
for i in range(5):
    try:
        mysqls.put(MySQLdb.connect(user='item_found', passwd='redbull', db='tf2mv'))
    except: pass

@app.route('/itemFound', methods=['POST'])
def itemFound():
    try:
        mysql = mysqls.get(block=False)
    except Queue.Empty:
        app.logger.error('Not enough mysql connections.')
        return
    try:
        cursor = mysql.cursor()
        cursor.execute('insert into item_found values (INET_ATON(?), NULL, ?, ?, ?, ?, ?)',
                       (request.ip, request.form['steamid'], request.form['method'],
                        request.form['quality'], request.form['item'], request.form['propername']))
        cursor.close()
        mysql.commit()
        mysqls.put(mysql)
    except Exception as e:
        app.logger.error(e)
    return
