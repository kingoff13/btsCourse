from bitshares.market import Market
from bitshares import exceptions as BTSExceptions
from requests import get
import time
import os
import yaml
from init import DBDriver

#sudo docker run -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=notalchemy -d mysql:latest
#sudo docker container start mysql-server

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
  conf = yaml.safe_load(f.read())
sql_conf=conf.get('sql')
assets = conf.get('assets')
dbConnector = DBDriver(sql_conf)

def formQuery(arQuery):
    result_query=''
    result_query = result_query + ("INSERT INTO p2pbridge_exchange_rates (SOURCE, DATETIME, ASSET1, ASSET2, VALUE) VALUES ")
    for trade in arQuery:
        #if 'inf' in str(trade): continue #print(str(trade))
        #trade['base_amount'] = str(trade['base']).split()[0].replace(',','')
        #trade['base_lit'] = str(trade['base']).split()[1]
        #trade['quote_amount'] = str(trade['quote']).split()[0].replace(',','')
        #trade['quote_lit'] = str(trade['quote']).split()[1]
        #values = "('{time}','{base_lit}', {base_amount}, '{quote_lit}', {quote_amount}, {price}), ".format(**trade)
        try: trade['base'] = asset_ids[trade['base']]
        except: trade['base'] = 0
        try: trade['quote'] = asset_ids[trade['quote']]
        except: trade['quote'] = 0
        values = "('{}', '{}', '{}', '{}', {}), ".format(trade['source'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), trade['base'], trade['quote'], trade['value'])
        result_query+=values
    result_query = result_query.rstrip(', ')
    print(result_query)
    return result_query

#format time: 'YYYY-MM-DDTHH:MM:SS'
def gettrades(market, start=False, stop=False):
    step=3000
    result={}
    result['quote_amount']=0
    result['base_amount']=0
    if stop==False: stop=time.time()
    else: stop=time.mktime(time.strptime(stop,'%Y-%m-%dT%X'))-time.timezone
    if start==False: start=stop-259200
    else: start=time.mktime(time.strptime(start,'%Y-%m-%dT%X'))-time.timezone
    while stop-step>start:
        trades = market.trades(limit=100, start=stop-step, stop=stop)
        if len(trades)<100:
            stop=stop-step
            print(time.strftime('%Y.%m.%d %X', time.localtime(stop)),
                  len(trades),
                  step,
                  '*2')
            step=step*2
            for trade in trades:
                result['quote_amount']+=float(str(trade['quote']).split()[0].replace(',',''))
                result['base_amount']+=float(str(trade['base']).split()[0].replace(',',''))
            if result['quote_amount']>1000: break
        elif len(trades)==100:
            print(time.strftime('%Y.%m.%d %X', time.localtime(stop)),
                  len(trades),
                  step,
                  '/2')
            step=step/2
            if step<1:
                stop=stop-1
    if result['base_amount']>result['quote_amount']:
        course = result['base_amount']/result['quote_amount']
        base_lit = market['base']['symbol']
        quote_lit = market['quote']['symbol']
    else:
        course = result['quote_amount']/result['base_amount']
        base_lit = market['quote']['symbol']
        quote_lit = market['base']['symbol']
    return {'source':'Bitshares',
            'base':base_lit,
            'quote':quote_lit,
            'value':course}

def getDataFromBitshares(pair):
    try:
        market = Market("{}:{}".format(pair[0], pair[1]))
    except BTSExceptions.AssetDoesNotExistsException:
        #raise Exception("")
        print("{}:{}".format(pair[0], pair[1]) + "notexist")
        return
    return gettrades(market)

def getDataFromCoinmarketcap(ids, convert=False):
    result=[]
    work={}
    r = get('https://api.coinmarketcap.com/v2/listings/').json()
    if isinstance(ids, list):
        for key,asset in enumerate(ids):
            for value in r['data']:
                if value['symbol']==asset:
                    work[asset]=value['id']
        for key,asset in work.items():
            r = get('https://api.coinmarketcap.com/v2/ticker/'+str(asset),
                    {'convert':convert}).json()
            result.append({'source':'Coinmarketcap',
                           'base':'USD',
                           'quote':key,
                           'value':r['data']['quotes']['USD']['price']})
    return result

def getAssetsFromMySQL():
    result={}
    query = "SELECT id, asset_id, symbol FROM p2pbridge_assets WHERE ACTIVE='Y'"
    dbConnector.cursor.execute(query)
    assets = dbConnector.cursor.fetchall()
    for asset in assets:
        result[asset[2]]=asset[0]
    return result

asset_ids = getAssetsFromMySQL()
dataCourses = getDataFromCoinmarketcap(assets['coinmarketcap'])
for asset in assets['bitshares']:
    dataCourses.append(getDataFromBitshares(('USD', asset)))
print(dataCourses)
query = formQuery(dataCourses)
dbConnector.cursor.execute(query)
dbConnector.cnx.commit()

#query = "SELECT datetime, base, base_amount, quote, quote_amount, price FROM courses"
#cursor.execute(query)

#for (datetime, base, base_amount, quote, quote_amount, price) in cursor:
#    print("{} {} {} {} {} {}".format(
#        datetime, base, base_amount, quote, quote_amount, price))

#print(cursor.fetchall()[0][0].timestamp())
dbConnector.cursor.close()
dbConnector.cnx.close()
