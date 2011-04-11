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
    addedTrades = 0
    cursor = db.cursor()
    cursor.execute("""
    select t1.timestamp, t1.player, t2.player, t1.id, t2.id
    from itemsRecieved t1
    join itemsRecieved t2
    on t1.timestamp between datetime(t2.timestamp, '-3 seconds') and datetime(t2.timestamp, '3 seconds')
    where t1.player < t2.player;
    """)
    for (k, g) in itertools.groupby(cursor.fetchall(), lambda t: t[1:3]):
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
        addedTrades += 1
    db.commit()
    print >> sys.stderr, 'Added {0} trades.'.format(addedTrades)

bannedItems = set([
    'A Carefully Wrapped Gift',
    'Samur-Eye',
    'Medi Gun',
    'Shotgun',
    ])
weapons = [
    "Loch-n-Load",
    "Buffalo Steak Sandvich",
    "Half-Zatoichi",
    "Crusader's Crossbow",
    "Fan O'War",
    "The Sandvich",
    "Your Eternal Reward",
    "The Sydney Sleeper",
    "The Powerjack",
    "The Blutsauger",
    "The Bushwacka",
    "The Kritzkrieg",
    "The Homewrecker",
    "Mad Milk",
    "The Scottish Resistance",
    "Natascha",
    "Conniver's Kunai",
    "The Dalokohs Bar",
    "The Dead Ringer",
    "Back Scratcher",
    "The Vita-Saw",
    "Amputator",
    "Bonk! Atomic Punch",
    "The Force-A-Nature",
    "The Equalizer",
    "The Gunboats",
    "The Gunslinger",
    "The Huntsman",
    "The Wrangler",
    "The Black Box",
    "The Degreaser",
    "Crit-a-Cola",
    "The Direct Hit",
    "The Ubersaw",
    "The Pain Train",
    "Claidheamohmor",
    "The Sandman",
    "The Chargin' Targe",
    "The Tribalman's Shiv",
    "The Axtinguisher",
    "The Razorback",
    "The Buff Banner",
    "Darwin's Danger Shield",
    "The Cloak and Dagger",
    "Candy Cane",
    "The Eyelander",
    "Jag",
    "Class Token",
    "Ullapool Caber",
    "The Shortstop",
    "Jarate",
    "Fists of Steel",
    "The Southern Hospitality",
    "Concheror",
    "Brass Beast",
    "The Frontier Justice",
    "Class Token",
    "The Holy Mackerel",
    "The Killing Gloves of Boxing",
    "Boston Basher",
    ]

substituteItems = {
    'Reclaimed Metal': (1/3., 'Refined Metal'),
    'Scrap Metal': (1/9., 'Refined Metal'),

    'Class Token - Scout':   (1, 'Class Token'),
    'Class Token - Soldier': (1, 'Class Token'),
    'Class Token - Pyro':    (1, 'Class Token'),
    'Class Token - Demoman': (1, 'Class Token'),
    'Class Token - Heavy':   (1, 'Class Token'),
    'Class Token - Engineer':(1, 'Class Token'),
    'Class Token - Medic':   (1, 'Class Token'),
    'Class Token - Sniper':  (1, 'Class Token'),
    'Class Token - Spy':     (1, 'Class Token'),

    'Slot Token - Primary':  (1, 'Slot Token'),
    'Slot Token - Secondary':(1, 'Slot Token'),
    'Slot Token - Melee':    (1, 'Slot Token'),

    'Scout Mask':   (1, 'Class Halloween Mask'),
    'Soldier Mask': (1, 'Class Halloween Mask'),
    'Pyro Mask':    (1, 'Class Halloween Mask'),
    'Demoman Mask': (1, 'Class Halloween Mask'),
    'Heavy Mask':   (1, 'Class Halloween Mask'),
    'Engineer Mask':(1, 'Class Halloween Mask'),
    'Medic Mask':   (1, 'Class Halloween Mask'),
    'Sniper Mask':  (1, 'Class Halloween Mask'),
    'Spy Mask':     (1, 'Class Halloween Mask'),
    }

for weapon in weapons:
    substituteItems[weapon] = (1, 'Any Weapon')

def computeMannconomyMatrix():
    cursor = db.cursor()
    cursor.execute('select distinct item from itemsRecieved')
    itemNames = set(row[0] for row in cursor.fetchall())
    itemNames -= bannedItems
    itemNames -= set(substituteItems.keys())
    itemNames |= set(item for (val, item) in substituteItems.values())
    items = dict(zip(itemNames, itertools.count()))

    n = len(items)
    refined = items['Refined Metal']

    A = scipy.zeros((1,n))

    cursor.execute('''
    select ti.trade,i.player,i.item
    from tradeItems ti
    join itemsRecieved i
    on ti.item = i.id
    where trade not in
      (select trade from tradeItems out
       where (select count(*) from tradeItems inn where out.item = inn.item) > 1)
    order by ti.trade, i.player''')
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

    x = scipy.optimize.nnls(A, b)[0]
    resid = scipy.dot(A, x)
    resid[0] = 0 # residual on first equation (refined = refined) doesn't count

    sortedResid = list(sorted(abs(resid)))
    threshold = 2/3. * x[refined] #sortedResid[int(round(0.80 * len(sortedResid)))]
    for r in range(len(A)):
        if resid[r] > threshold:
            A[r] = 0
            A[0][refined] = 1
            b[r] = 1
    scaledThreshold = threshold / x[refined]

    df = n - scipy.linalg.lstsq(A, b)[2]
    x = scipy.optimize.nnls(A, b)[0]

    zeroCount = len([val for val in x if val < 1e-6])
    print >> sys.stderr, 'Tracking {0} items, {1} have value 0.00.'.format(n, zeroCount)
    print >> sys.stderr, 'Ignoring trades imbalanced by more than {0:.2f} refined metal.'.format(scaledThreshold)
    if df:
        if df == 1:
            print >> sys.stderr, '1 degree of freedom remains.'
        else:
            print >> sys.stderr, '{0} degrees of freedom remain.'.format(df)

    for (item, value) in sorted(zip(itemNames, x / x[refined]), key=lambda t: -t[1]):
        if value >= 0.01:
            print '{0:45s}{1:.2f}'.format(item, value)

def sign(n):
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1

#getNewData()
#correlateTrades()
computeMannconomyMatrix()

# All trades involving a particular item name.
#select * from tradeItems ti join itemsRecieved ir on ti.item = ir.id where ti.trade in (select trade from tradeItems join itemsRecieved on tradeItems.item = itemsRecieved.id where itemsRecieved.item like '%Hue%');
