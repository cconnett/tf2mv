import re
import urllib2
import sqlite3
import codecs
import itertools
import scipy
import scipy.linalg
from pprint import pprint

db = sqlite3.connect('mv.db')

def getNewData():
    tradesPage = urllib2.urlopen('http://tradingpost.dynamitealley.com/trade.php').read()
    #tradesPage = open('Team Fortress 2 Trading Post.html').read()
    tradesPage = codecs.getdecoder('latin-1')(tradesPage)[0]

    itemRecieved = re.compile(r'^.*?;(.*?)<.*?;(.*?)<.*?;(.*?)<.*?;(.*?)<.*$',re.M)

    cursor = db.cursor()
    cursor.executemany('insert or ignore into itemsRecieved values (?, ?, ?, ?)',
                       itemRecieved.findall(tradesPage))

    db.commit()

def correlateTrades():
    cursor = db.cursor()
    cursor.execute("select t1.timestamp, t1.player, t2.player, t1.id, t2.id from itemsRecieved t1 join itemsRecieved t2 on t1.player < t2.player where datetime(t1.timestamp) between datetime(t2.timestamp, '-3 seconds') and datetime(t2.timestamp, '3 seconds')")
    for (k, g) in itertools.groupby(cursor.fetchall(), lambda t: t[:3]):
        try:
            cursor.execute('insert or abort into trades values (NULL, ?, ?)', (k[0], k[1]))
        except sqlite3.IntegrityError:
            continue
        trade = cursor.lastrowid
        items = set()
        for (time, p1, p2, i1, i2) in g:
            items.add(i1)
            items.add(i2)
        cursor.executemany('insert into tradeItems values (?, ?)',
                           [(trade, i) for i in items])
    db.commit()

def computeMannconomyMatrix():
    cursor = db.cursor()
    cursor.execute('select distinct item from itemsRecieved')
    itemNames = [row[0] for row in cursor.fetchall()]
    items = dict(zip(itemNames, itertools.count()))
    n = len(items)

    A = scipy.zeros((n,n))
    #A[items['Refined Metal']][items['Refined Metal']] += 1

    cursor.execute('select ti.trade,i.player,i.item from tradeItems ti join itemsRecieved i on ti.item = i.id order by ti.trade, i.player')
    rows = cursor.fetchall()
    for (_, g) in itertools.groupby(rows, lambda r: r[0]):
        tradeSummary = scipy.zeros(n)
        affectedItems = set()
        inc = 1
        for (player, playersItemRows) in itertools.groupby(g, lambda r: r[1]):
            for (_, _, item) in playersItemRows:
                affectedItems.add(item)
                tradeSummary[items[item]] += inc
            inc = -1
        #print tradeSummary
        for affectedItem in affectedItems:
            index = items[affectedItem]
            A[index] += sign(tradeSummary[index]) * tradeSummary
    x = scipy.linalg.lstsq(A, scipy.zeros(n))
    print x
    #x = scipy.linalg.eig(A)[1][-1]
    #for (item, value) in zip(itemNames, x / x[items['Refined Metal']]):
    #    print '{0:45s}{1:s}'.format(item, value)

def sign(n):
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1

#getNewData()
#correlateTrades()
computeMannconomyMatrix()
