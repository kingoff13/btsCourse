from bitshares.market import Market
from bitshares import exceptions as BTSExceptions
import bitshares as bts 
from requests import get
from lxml import objectify
import time
from grapheneapi.exceptions import NumRetriesReached
import os
import yaml
import traceback
from models import Rate, RateValue, Session
from init import DBDriver

class MyInstance():
    instance=None
    config={}

# sudo docker run -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=notalchemy -d mysql:latest
# sudo docker container start mysql-server
# sudo docker exec -it mysql-server mysql -uroot -pnotalchemy --database=bitshares

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
  conf = yaml.safe_load(f.read())
sql_conf = conf.get('sql')
check_interval = conf.get('check_interval', 300)

session = Session()

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
    return course


def getDataFromBitshares(base, quote='USD'):
    MyInstance.config={'node': 'bitshares.crypto.fans'}
    MyInstance.instance = bts.BitShares(**MyInstance.config)
    tries=0
    market=None
    while market==None:
        try:
            market = Market("UDS:BTS", bitshares_instance=MyInstance.instance)
        except NumRetriesReached:
            print('websocket closed. Try reconnect '+str(tries))
            time.sleep(5)
            tries+=1
            if tries>10:
                print('Fall connect')
                return
        except BTSExceptions.AssetDoesNotExistsException:
            # raise Exception("")
            print("{}:{}".format(base, quote) + "notexist")
            return
    return gettrades(market)


def getDataFromCoinmarketcap(base, quote='USD'):
    r = get('https://api.coinmarketcap.com/v2/ticker/'+str(base),
            {'convert': quote}).json()
    try:
        result = r['data']['quotes'][quote]['price']
    except:
        print("{}:{}".format(base, quote) + "notexist")
        return
    return result

def getDataFromCBR(base, quote='USD'):
    if (quote=='RUB' or quote=='RUR') and __CbrfMoexAssocTable[base]:
        f = get('http://www.cbr.ru/scripts/XML_daily.asp')
        xmltest = objectify.fromstring(f.content)
        result = []
        for valute in xmltest.Valute:
            if valute.CharCode == __CbrfMoexAssocTable[base]['CBRF']['NAME']:
                return float(str(valute.Value).replace(',','.'))/__CbrfMoexAssocTable[base]['CBRF']['PREC']
    else:
        return

def getDataFromMoex(base, quote='USD'):
    if (quote=='RUB' or quote=='RUR') and __CbrfMoexAssocTable[base]:
        f = get('https://iss.moex.com/iss/engines/currency/markets/selt/boards/cets/securities.xml?securities=USD000000TOD,EUR_RUB__TOM,CNYRUB_TOM,EURUSD000TOM')
        xmltest = objectify.fromstring(f.content)
        for row in xmltest.data[1].rows.row:
            if row.attrib['SECID'] == __CbrfMoexAssocTable[base]['MOEX']['NAME'] and row.attrib['LAST']:
                return float(row.attrib['LAST'])
    else:
        return

def getDataFromImf(quote, base='SDR'):
    f = get('http://www.imf.org/external/np/fin/data/rms_mth.aspx?reportType=CVSDR&tsvflag=Y')
    for row in f.text.split("\r\n"):
        values = row.split("\t")
        if values[0]==quote:
            return float(values.pop().replace(',',''))
    return

def process_loop(check_interval=300):
    while True:
        rates = session.query(Rate).filter_by(active = 'Y').all()
        dataCourses = []
        for rate in rates:
            if rate.source =='bitshares':
                try:
                    a = getDataFromBitshares(rate.base_asset.asset_id, rate.quote_asset.asset_id)
                    if a:
                        dataCourses.append(RateValue(rate.id, a))
                        session.query(RateValue).\
                            filter(RateValue.rate_id == rate.id, RateValue.active == 'Y').\
                            update({RateValue.active: 'N'})
                except Exception:
                    print(traceback.format_exc())
            if rate.source =='coinmarketcap':
                try:
                    a = getDataFromCoinmarketcap(rate.base_asset.coinmarketcap_id, rate.quote_asset.coinmarketcap_code)
                    if a:
                        dataCourses.append(RateValue(rate.id, a))
                        session.query(RateValue).\
                            filter(RateValue.rate_id == rate.id, RateValue.active == 'Y').\
                            update({RateValue.active: 'N'})
                except Exception:
                    print(traceback.format_exc())
            if rate.source =='cbrf':
                try:
                    a = getDataFromCBR(rate.base_asset.symbol, rate.quote_asset.symbol)
                    if a:
                        dataCourses.append(RateValue(rate.id, a))
                        session.query(RateValue).\
                            filter(RateValue.rate_id == rate.id, RateValue.active == 'Y').\
                            update({RateValue.active: 'N'})
                except Exception:
                    print(traceback.format_exc())
            if rate.source =='mmvb':
                try:
                    a = getDataFromMoex(rate.base_asset.symbol, rate.quote_asset.symbol)
                    if a:
                        dataCourses.append(RateValue(rate.id, a))
                        session.query(RateValue).\
                            filter(RateValue.rate_id == rate.id, RateValue.active == 'Y').\
                            update({RateValue.active: 'N'})
                except Exception:
                    print(traceback.format_exc())
            if rate.source =='imf':
                try:
                    a = getDataFromImf(rate.quote_asset.imf_name)
                    if a:
                        dataCourses.append(RateValue(rate.id, a))
                        session.query(RateValue).\
                            filter(RateValue.rate_id == rate.id, RateValue.active == 'Y').\
                            update({RateValue.active: 'N'})
                except Exception:
                    print(traceback.format_exc())
        session.add_all(dataCourses)
        session.commit()
        time.sleep(check_interval)

process_loop(check_interval)
