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

__CbrfMoexAssocTable = {
    'USD' : {
        'CBRF' : {
            'NAME' : 'USD',
            'PREC' : 1
        },
        'MOEX' : {
            'NAME' : 'USD000000TOD'
        }
    },
    'CNY' : {
        'CBRF' : {
            'NAME' : 'CNY',
            'PREC' : 10
        },
        'MOEX' : {
            'NAME' : 'CNYRUB_TOM'
        }
    },
    'EUR' : {
        'CBRF' : {
            'NAME' : 'EUR',
            'PREC' : 1
        },
        'MOEX' : {
            'NAME' : 'EUR_RUB__TOM'
        }
    },
    'EURO' : {
        'CBRF' : {
            'NAME' : 'EUR',
            'PREC' : 1
        },
        'MOEX' : {
            'NAME' : 'EUR_RUB__TOM'
        }
    }
}

def formQuery(arQuery):
    result_query = ''
    result_query = result_query + ("INSERT INTO p2pbridge_exchange_rates_values "
                                   "(RATE_ID, DATETIME, VALUE, ACTIVE) "
                                   "VALUES ")
    for trade in arQuery:
        values = "({}, '{}', {}, '{}'), ".format(
            trade['rate_id'],
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())),
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
    return {'value': course}


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
    try:
        result = ({'value': r['data']['quotes'][quote]['price']})
    except:
        print("{}:{}".format(base, quote) + "notexist")
        return
    return result

def getDataFromCBR(base, quote='USD'):
    if (base=='RUB' or base=='RUR') and __CbrfMoexAssocTable[quote]:
        f = get('http://www.cbr.ru/scripts/XML_daily.asp')
        xmltest = objectify.fromstring(f.content)
        result = []
        for valute in xmltest.Valute:
            if valute.CharCode == __CbrfMoexAssocTable[quote]['CBRF']['NAME']:
                return {'value': float(str(valute.Value).replace(',','.'))/__CbrfMoexAssocTable[quote]['CBRF']['PREC']}
    else:
        return

def getDataFromMoex(base, quote='USD'):
    if (base=='RUB' or base=='RUR') and __CbrfMoexAssocTable[quote]:
        f = get('https://iss.moex.com/iss/engines/currency/markets/selt/boards/cets/securities.xml?securities=USD000000TOD,EUR_RUB__TOM,CNYRUB_TOM,EURUSD000TOM')
        xmltest = objectify.fromstring(f.content)
        result = []
        for row in xmltest.data[1].rows.row:
            if row.attrib['SECID'] == __CbrfMoexAssocTable[quote]['MOEX']['NAME'] and row.attrib['LAST']:
                return {
                'value': float(row.attrib['LAST'])
            }
        return result
    else:
        return

def getBtsRatesFromMySQL(dbConnector):
    result = []
    query = ("SELECT "
             "rates.ID, "
             "rates.SOURCE, "
             "base_assets.SYMBOL AS BASE_SYMBOL, "
             "base_assets.ASSET_ID AS BASE_BTS_ID, "
             "base_assets.COINMARKETCAP_ID AS BASE_CMC_ID, "
             "base_assets.COINMARKETCAP_CODE AS BASE_CMC_CODE, "
             "quote_assets.SYMBOL AS QUOTE_SYMBOL, "
             "quote_assets.ASSET_ID AS QUOTE_BTS_ID, "
             "quote_assets.COINMARKETCAP_ID AS QUOTE_CMC_ID, "
             "quote_assets.COINMARKETCAP_CODE AS QUOTE_CMC_CODE "
             "FROM p2pbridge_exchange_rates_meta AS rates "
             "LEFT JOIN p2pbridge_assets base_assets "
             "ON rates.BASE_ASSET_ID=base_assets.ID "
             "LEFT JOIN p2pbridge_assets quote_assets "
             "ON rates.QUOTE_ASSET_ID=quote_assets.ID "
             "WHERE rates.ACTIVE='Y'")
    dbConnector.cursor.execute(query)
    rates = dbConnector.cursor.fetchall()
    for rate in rates:
        result.append({'id': rate[0],
                       'source': rate[1],
                       'base_symbol': rate[2],
                       'base_id_bts': rate[3],
                       'base_id_cmc': rate[4],
                       'base_code_cmc': rate[5],
                       'quote_symbol': rate[6],
                       'quote_id_bts': rate[7],
                       'quote_id_cmc': rate[8],
                       'quote_code_cmc': rate[9]})
    return result


def process_loop(check_interval=300):
    while True:
        dbConnector = DBDriver(sql_conf)
        rates_ids = getBtsRatesFromMySQL(dbConnector )
        dataCourses = []
        for rate in rates_ids:
            if rate['source']=='bitshares':
                a = getDataFromBitshares(rate['base_id_bts'], rate['quote_id_bts'])
                if a:
                    a.update({'rate_id': rate['id']})
                    dataCourses.append(a)
            if rate['source']=='coinmarketcap':
                a = getDataFromCoinmarketcap(rate['base_id_cmc'], rate['quote_code_cmc'])
                if a:
                    a.update({'rate_id': rate['id']})
                    dataCourses.append(a)
            if rate['source']=='cbrf':
                a = getDataFromCBR(rate['base_symbol'], rate['quote_symbol'])
                if a:
                    a.update({'rate_id': rate['id']})
                    dataCourses.append(a)
            if rate['source']=='mmvb':
                a = getDataFromMoex(rate['base_symbol'], rate['quote_symbol'])
                if a:
                    a.update({'rate_id': rate['id']})
                    dataCourses.append(a)
        query = "UPDATE p2pbridge_exchange_rates_values SET ACTIVE='N' WHERE ACTIVE='Y'"
        dbConnector.cursor.execute(query)
        dbConnector.cnx.commit()
        query = formQuery(dataCourses)
        dbConnector.cursor.execute(query)
        dbConnector.cnx.commit()
        dbConnector.cursor.close()
        dbConnector.cnx.close()
        time.sleep(check_interval)

process_loop(check_interval)
