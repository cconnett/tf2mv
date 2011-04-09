import re
import urllib2
import sqlite3
import codecs
import itertools
import scipy
import scipy.linalg
import scipy.optimize
import sys
from pprint import pprint

db = sqlite3.connect('mv.db')

def getNewData():
    tradesPage = urllib2.urlopen('http://tradingpost.dynamitealley.com/trade.php').read()
    tradesPage = codecs.getdecoder('latin-1')(tradesPage)[0]

    itemRecieved = re.compile(r'^.*?;(.*?)<.*?;(.*?)<.*?;(.*?)<.*?;(.*?)<.*$',re.M)

    cursor = db.cursor()
    cursor.executemany('insert or ignore into itemsRecieved values (?, ?, ?, ?)',
                       itemRecieved.findall(tradesPage))

    db.commit()

def correlateTrades():
    completedTrades = 0
    cursor = db.cursor()
    cursor.execute("""
    select t1.timestamp, t1.player, t2.player, t1.id, t2.id
    from itemsRecieved t1
    join itemsRecieved t2
    where t1.player < t2.player
    and datetime(t1.timestamp) between datetime(t2.timestamp, '-3 seconds') and datetime(t2.timestamp, '3 seconds')
    """)
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
        completedTrades += 1
    db.commit()
    print >> sys.stderr, 'Completed {0} trades.'.format(completedTrades)

bannedItems = set(['A Carefully Wrapped Gift'])
substituteItems = {
    'Reclaimed Metal': (1/3., 'Refined Metal'),
    'Scrap Metal': (1/9., 'Refined Metal'),
    }

def computeMannconomyMatrix():
    cursor = db.cursor()
    cursor.execute('select distinct item from itemsRecieved')
    itemNames = set(row[0] for row in cursor.fetchall())
    itemNames -= bannedItems
    itemNames -= set(substituteItems.keys())
    items = dict(zip(itemNames, itertools.count()))

    n = len(items)
    refined = items['Refined Metal']

    A = scipy.zeros((1,n))

    cursor.execute('select ti.trade,i.player,i.item from tradeItems ti join itemsRecieved i on ti.item = i.id order by ti.trade, i.player')
    rows = cursor.fetchall()
    for (_, g) in itertools.groupby(rows, lambda r: r[0]):
        tradeSummary = scipy.zeros(n)
        tradeSummary.shape = (1, n)
        coeff = 1
        try:
            for (player, playersItemRows) in itertools.groupby(g, lambda r: r[1]):
                for (_, _, item) in playersItemRows:
                    if item in bannedItems:
                        raise ValueError('Banned item')
                    num, item = substituteItems.get(item, (1, item))
                    tradeSummary[0][items[item]] += coeff * num
                coeff = -1
        except ValueError:
            continue
        A = scipy.concatenate((A, tradeSummary))
    m = A.shape[0]
    b = scipy.zeros(m)


    A[0][refined] = 1

    b[0] = 1

    df = n - scipy.linalg.lstsq(A, b)[2]
    if df:
        if df == 1:
            print >> sys.stderr, '1 degree of freedom remains.'
        else:
            print >> sys.stderr, '{0} degrees of freedom remain.'.format(df)
    x = scipy.optimize.nnls(A, b)[0]
    #print x
    for (item, value) in sorted(zip(itemNames, x / x[refined]), key=lambda t: -t[1]):
        print '{0:45s}{1:.2f}'.format(item, value)
        pass

def sign(n):
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1

getNewData()
correlateTrades()
computeMannconomyMatrix()
