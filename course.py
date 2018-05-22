from bitshares.market import Market
import time
import os
import yaml
import mysql.connector
from pprint import pprint

#sql_map:
TABLES = {}
TABLES['courses'] = (
  "CREATE TABLE `courses` ("
  "  `id` int NOT NULL AUTO_INCREMENT,"
  "  `datetime` datetime NOT NULL,"
  "  `base` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci',"
  "  `base_amount` double NOT NULL,"
  "  `quote` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci',"
  "  `quote_amount` double NOT NULL,"
  "  `price` double NOT NULL,"
  "  PRIMARY KEY (`id`)" 
#  "  INDEX (base),"
#  "  INDEX (quote),"
#  "  FOREIGN KEY (base) REFERENCES p2pbridge_assets (symbol) ON DELETE RESTRICT ON UPDATE CASCADE,"
#  "  FOREIGN KEY (quote) REFERENCES p2pbridge_assets (symbol) ON DELETE RESTRICT ON UPDATE CASCADE"
  ") ENGINE=InnoDB")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
  conf = yaml.safe_load(f.read())
sql_conf=conf.get('sql')
market = Market("USD:BTS")
#(2018-05-20 17:37:24) 0.0000 USD 0.00000 BTS @ inf BTS/USD
#(2018-05-21 04:59:57) 0.0000 USD 0.00000 BTS @ inf BTS/USD
#(2018-05-21 13:28:42) 0.0000 USD 0.00000 BTS @ inf BTS/USD

def formQuery(arTrades):
    result_query=''
    result_query = result_query + ("INSERT INTO courses (datetime, base, base_amount, quote, quote_amount, price) VALUES ")
    arTrades.reverse()
    for trade in arTrades:
        hole = str(trade).find('inf')
        if hole!=-1: print(str(trade))
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
def gettrades(start=False, stop=False):
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
            #print(time.strftime('%Y.%m.%d %X', time.localtime(stop)), len(trades), step, '*2')
            step=step*2
            result.extend(trades)
        elif len(trades)==100:
            #print(time.strftime('%Y.%m.%d %X', time.localtime(stop)), len(trades), step, '/2')
            step=step/2
            if step<1:
                stop=stop-1
    trades = market.trades(limit=100, start=start+1, stop=stop)
    result.extend(trades)
    return result
 
#sudo docker run -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=notalchemy -d mysql:latest
#sudo docker container start mysql-server

########Data base connect######################
cnx = mysql.connector.connect(user=sql_conf['username'], password=sql_conf['password'], host=sql_conf['host'])#, database='bitshares')
cursor = cnx.cursor()
###############################################

#######Data base create if not exist###########
def create_database(cursor, dbname):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dbname))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = sql_conf['db']
except mysql.connector.Error as err:
    if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
       create_database(sql_conf['db'])
       cnx.database = sql_conf['db']
    else:
       print(err)
       exit(1)
###############################################

#######Tables create if not exist#############
for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
##############################################
query = "SELECT datetime FROM courses ORDER BY id DESC LIMIT 1"
cursor.execute(query)
values = cursor.fetchall()
if len(values )>0: time_last_deal = values[0][0].isoformat()
else: time_last_deal = time.strftime('%Y-%m-%dT%X',time.localtime(time.time() - 259200))
result = gettrades(time_last_deal)
if len(result)>0:
    query = formQuery(result)
    cursor.execute(query)
    cnx.commit()

query = "SELECT datetime, base, base_amount, quote, quote_amount, price FROM courses"
#cursor.execute(query)

#for (datetime, base, base_amount, quote, quote_amount, price) in cursor:
#    print("{} {} {} {} {} {}".format(
#        datetime, base, base_amount, quote, quote_amount, price))
#pprint(globals())

#print(cursor.fetchall()[0][0].timestamp())
cursor.close()
cnx.close()
