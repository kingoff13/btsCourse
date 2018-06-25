from bitshares.market import Market
from bitshares import exceptions as BTSExceptions
from requests import get
from lxml import objectify
import time
import os
import yaml
from init import DBDriver

# sudo docker run -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=notalchemy -d mysql:latest
# sudo docker container start mysql-server
# sudo docker exec -it mysql-server mysql -uroot -pnotalchemy --database=bitshares

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
  conf = yaml.safe_load(f.read())
sql_conf = conf.get('sql')
check_interval = conf.get('check_interval', 300)


def formQuery(arQuery):
    result_query = ''
    result_query = result_query + ("INSERT INTO p2pbridge_exchange_rates "
                                   "(SOURCE, DATETIME, ASSET1, ASSET2, VALUE, ACTIVE) "
                                   "VALUES ")
    for trade in arQuery:
        # if 'inf' in str(trade): continue #print(str(trade))
        # trade['base_amount'] = str(trade['base']).split()[0].replace(',','')
        # trade['base_lit'] = str(trade['base']).split()[1]
        # trade['quote_amount'] = str(trade['quote']).split()[0].replace(',','')
        # trade['quote_lit'] = str(trade['quote']).split()[1]
        # values = "('{time}', '{base_lit}', {base_amount}, '{quote_lit}', {quote_amount}, {price}), ".format(**trade)
        values = "('{}', '{}', '{}', '{}', {}, '{}'), ".format(
            trade['source'],
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()+18000)),
            trade['base'],
            trade['quote'],
            trade['value'],
            'Y')
        result_query += values
    result_query = result_query.rstrip(', ')
    return result_query


# format time: 'YYYY-MM-DDTHH:MM:SS'
def gettrades(market, start=False, stop=False):
    step = 3000
    result = {}
    result['quote_amount'] = 0
    result['base_amount'] = 0
    if stop is False:
        stop = time.time()
    else:
        stop = time.mktime(time.strptime(stop, '%Y-%m-%dT%X'))-time.timezone
    if start is False:
        start = stop-259200
    else:
        start = time.mktime(time.strptime(start, '%Y-%m-%dT%X'))-time.timezone
    while stop-step > start:
        trades = market.trades(limit=100, start=stop-step, stop=stop)
        if len(trades) < 100:
            stop = stop-step
            # print(time.strftime('%Y.%m.%d %X', time.localtime(stop)),
            #      len(trades),
            #      step,
            #      '*2')
            step = step*2
            for trade in trades:
                result['quote_amount'] += float(str(
                    trade['quote']).split()[0].replace(',', ''))
                result['base_amount'] += float(str(
                    trade['base']).split()[0].replace(',', ''))
            if result['base_amount'] > 1000:
                break
        elif len(trades) == 100:
            # print(time.strftime('%Y.%m.%d %X', time.localtime(stop)),
            #      len(trades),
            #      step,
            #      '/2')
            step = step/2
            if step < 1:
                stop = stop-1
    try:
        course = result['base_amount']/result['quote_amount']
    except:
        course = 0
    base_lit = market['base']['symbol']
    quote_lit = market['quote']['symbol']
    return {'source': 'Bitshares',
            'base': base_lit,
            'quote': quote_lit,
            'value': course}


def getDataFromBitshares(base, quote='USD'):
    try:
        market = Market("{}:{}".format(base, quote))
    except BTSExceptions.AssetDoesNotExistsException:
        # raise Exception("")
        print("{}:{}".format(base, quote) + "notexist")
        return
    return gettrades(market)


def getDataFromCoinmarketcap(base, quote='USD'):
    r = get('https://api.coinmarketcap.com/v2/ticker/'+str(base),
            {'convert': quote}).json()
    result = ({'source': 'Coinmarketcap',
               'base': quote,
               'quote': r['data']['symbol'],
               'value': r['data']['quotes'][quote]['price']})
    return result

def getDataFromCBR():
    f = get('http://www.cbr.ru/scripts/XML_daily.asp')
    xmltest = objectify.fromstring(f.content)
    result = []
    for valute in xmltest.Valute:
        if valute.CharCode == 'USD': result.append({
            'source': 'CBR',
            'base': 291,
            'quote': 292,
            'value': valute.Value
        })
        if valute.CharCode == 'EUR': result.append({
            'source': 'CBR',
            'base': 291,
            'quote': 294,
            'value': valute.Value
        })
        if valute.CharCode == 'CNY': result.append({
            'source': 'CBR',
            'base': 291,
            'quote': 295,
            'value': valute.Value
        })
    return result

def getDataFromMoex():
    f = get('https://iss.moex.com/iss/engines/currency/markets/selt/boards/cets/securities.xml?securities=USD000000TOD,EUR_RUB__TOM,CNYRUB_TOM,EURUSD000TOM')
    xmltest = objectify.fromstring(f.content)
    result = []
    for row in xmltest.data[1].rows.row:
        if row.attrib['SECID'] == 'USD000000TOD': result.append({
            'source': 'MOEX',
            'base': 291,
            'quote': 292,
            'value': row.attrib['LAST']
        })
        if row.attrib['SECID'] == 'EUR_RUB__TOM': result.append({
            'source': 'MOEX',
            'base': 291,
            'quote': 292,
            'value': row.attrib['LAST']
        })
        if row.attrib['SECID'] == 'CNYRUB_TOM': result.append({
            'source': 'MOEX',
            'base': 291,
            'quote': 292,
            'value': row.attrib['LAST']
        })
    return result

def getAssetsFromMySQL():
    dbConnector = DBDriver(sql_conf)
    result = []
    query = ("SELECT p2pbridge_assets.ID, p2pbridge_assets.ASSET_ID, p2pbridge_assets.SYMBOL, p2pbridge_assets.COINMARKETCAP_ID, p2pbridge_assets_type_blockchain.BLOCKCHAIN_ID "
             "FROM p2pbridge_assets LEFT JOIN p2pbridge_assets_type_blockchain "
             "ON p2pbridge_assets.ID=p2pbridge_assets_type_blockchain.ASSET_ID "
             "WHERE p2pbridge_assets.MONITOR='Y'")
    dbConnector.cursor.execute(query)
    assets = dbConnector.cursor.fetchall()
    for asset in assets:
        result.append({'id': asset[0],
                       'asset_id': asset[1],
                       'symbol': asset[2],
                       'coinmarketcap_id': asset[3],
                       'blockchain_id': asset[4]})
    dbConnector.cursor.close()
    dbConnector.cnx.close()
    return result


def process_loop(check_interval=300):
    while True:
        dbConnector = DBDriver(sql_conf)
        dataCourses = []
        for asset in asset_ids:
            if (isinstance(asset['coinmarketcap_id'], int) and asset['coinmarketcap_id']!=0):
                a = getDataFromCoinmarketcap(asset['coinmarketcap_id'], 'USD')
                a.update({'base': 292, 'quote': asset['id']})
                dataCourses.append(a)
                a = getDataFromCoinmarketcap(asset['coinmarketcap_id'], 'BTS')
                a.update({'base': 212, 'quote': asset['id']})
                dataCourses.append(a)
                a = getDataFromCoinmarketcap(asset['coinmarketcap_id'], 'KRM')
                a.update({'base': 296, 'quote': asset['id']})
                dataCourses.append(a)
            if (
                asset['asset_id'].strip() and
                asset['asset_id'] != '0' and
                asset['blockchain_id'] == 1
            ):
                a = getDataFromBitshares(asset['asset_id'], 'USD')
                a.update({'base': 230, 'quote': asset['id']})
                dataCourses.append(a)
                a = getDataFromBitshares(asset['asset_id'], 'BTS')
                a.update({'base': 212, 'quote': asset['id']})
                dataCourses.append(a)
                a = getDataFromBitshares(asset['asset_id'], 'RUDEX.KRM')
                a.update({'base': 296, 'quote': asset['id']})
                dataCourses.append(a)
        a = getDataFromCBR()
        dataCourses.extend(a)
        a = getDataFromMoex()
        dataCourses.extend(a)
        query = "UPDATE p2pbridge_exchange_rates SET ACTIVE='N' WHERE ACTIVE='Y'"
        dbConnector.cursor.execute(query)
        dbConnector.cnx.commit()
        query = formQuery(dataCourses)
        dbConnector.cursor.execute(query)
        dbConnector.cnx.commit()
        dbConnector.cursor.close()
        dbConnector.cnx.close()
        time.sleep(check_interval)


asset_ids = getAssetsFromMySQL()
process_loop(check_interval)
