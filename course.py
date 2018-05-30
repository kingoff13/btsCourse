from bitshares.market import Market
from bitshares import exceptions as BTSExceptions
from requests import get
import time
import os
import yaml
from pprint import pprint
from init import DBDriver

#sudo docker run -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=notalchemy -d mysql:latest
#sudo docker container start mysql-server

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
  conf = yaml.safe_load(f.read())
sql_conf=conf.get('sql')
assets = conf.get('assets')
dbConnector = DBDriver(sql_conf)

def formQuery(arTrades):
    result_query=''
    result_query = result_query + ("INSERT INTO courses (datetime, base, base_amount, quote, quote_amount, price) VALUES ")
    arTrades.reverse()
    for trade in arTrades:
        if 'inf' in str(trade): continue #print(str(trade))
        trade['base_amount'] = str(trade['base']).split()[0].replace(',','')
        trade['base_lit'] = str(trade['base']).split()[1]
        trade['quote_amount'] = str(trade['quote']).split()[0].replace(',','')
        trade['quote_lit'] = str(trade['quote']).split()[1]
        #values = "('{time}','{base_lit}', {base_amount}, '{quote_lit}', {quote_amount}, {price}), ".format(**trade)
        values = "('{}','{}', {}, '{}', {}, {}), ".format(trade['time'], trade['base_lit'], trade['base_amount'], trade['quote_lit'], trade['quote_amount'], trade['price'])
        result_query=result_query+values
    result_query = result_query.rstrip(', ')
    return result_query

#format time: 'YYYY-MM-DDTHH:MM:SS'
def gettrades(market, start=False, stop=False):
    step=3000
    result=[]
    trades=[]
    if stop==False: stop=time.time()
    else: stop=time.mktime(time.strptime(stop,'%Y-%m-%dT%X'))-time.timezone
    if start==False: start=stop-3
    else: start=time.mktime(time.strptime(start,'%Y-%m-%dT%X'))-time.timezone
    while stop-step>start:
        trades = market.trades(limit=100, start=stop-step, stop=stop)
        if len(trades)<100:
            stop=stop-step
            print(time.strftime('%Y.%m.%d %X', time.localtime(stop)), len(trades), step, '*2')
            step=step*2
            result.extend(trades)
        elif len(trades)==100:
            print(time.strftime('%Y.%m.%d %X', time.localtime(stop)), len(trades), step, '/2')
            step=step/2
            if step<1:
                stop=stop-1
    trades = market.trades(limit=100, start=start+1, stop=stop)
    result.extend(trades)
    return result

def getDataFromBitshares(pair):
    try:
        market = Market("{}:{}".format(pair[0], pair[1]))
    except BTSExceptions.AssetDoesNotExistsException:
        #raise Exception("")
        print("{}:{}".format(pair[0], pair[1]) + "notexist")
        return
    query = "SELECT datetime FROM courses WHERE base='{}' AND quote='{}' ORDER BY id DESC LIMIT 1".format(pair[0], pair[1])
    dbConnector.cursor.execute(query)
    values = dbConnector.cursor.fetchall()
    if len(values)>0: time_last_deal = values[0][0].isoformat()
    else: time_last_deal = time.strftime('%Y-%m-%dT%X',time.localtime(time.time() - 259200))
    result = gettrades(market, time_last_deal)
    if len(result)>0:
        query = formQuery(result)
        dbConnector.cursor.execute(query)
        dbConnector.cnx.commit()
        print('done')

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
            r = get('https://api.coinmarketcap.com/v2/ticker/'+str(asset), {'convert':convert}).json()
            result.append({key:r['data']['quotes']['USD']['price']})
    return result

def getAssetsFromMySQL():
    query = "SELECT id, asset_id, symbol FROM p2pbridge_assets WHERE ACTIVE='Y'"
    dbConnector.cursor.execute(query)
    assets = dbConnector.cursor.fetchall()
    pairs=[]
    for i in range(len(assets)-1):
        item = assets.pop(0)
        for value in assets:
            base=item[1] if (item[1].strip() and item[1]!='0') else item[2]
            quote=value[1] if (value[1].strip() and value[1]!='0') else value[2]
            pairs.append((base,quote))

#getDataFromCoinmarketcap()
dataCMC = getDataFromCoinmarketcap(assets['coinmarketcap'])
print(dataCMC)
for asset in assets['bitshares']:
    getDataFromBitshares(('USD', asset))

#print('\n'.join(pairs))

#query = "SELECT datetime, base, base_amount, quote, quote_amount, price FROM courses"
#cursor.execute(query)

#for (datetime, base, base_amount, quote, quote_amount, price) in cursor:
#    print("{} {} {} {} {} {}".format(
#        datetime, base, base_amount, quote, quote_amount, price))
#pprint(globals())

#print(cursor.fetchall()[0][0].timestamp())
dbConnector.cursor.close()
dbConnector.cnx.close()
