# from bitshares.blockchain import Blockchain
# from time import time
# test = Blockchain()
import mysql.connector

def recprint(array):
  global tab
  try:
    tab
  except:
    tab=0
  tab+=1
  if (isinstance(array, dict)):
    for key, value in array.items():
      if not (isinstance(value, dict) or isinstance(value, list)):
        print('  '*tab+str(key)+' : '+str(value))
      else:
        print('  '*tab+str(key)+' : ')
        recprint(value)
  elif (isinstance(array, list)):
    i=0
    for value in array:
      i+=1
      if not (isinstance(value, dict) or isinstance(value, list)):
        print('  '*tab+str(i)+' : '+str(value))
      else:
        print('  '*tab+str(i)+' : ')
        recprint(value)
  tab-=1

def showOperationsInBlock(block):
  global count
  try:
    count
  except:
    count = {}
  for transaction in block['transactions']:
    for operation in transaction['operations']:
      try:
        count[operation[0]]
      except:
        count[operation[0]]=1
      else:
        count[operation[0]]=count[operation[0]]+1
      print(count)
  return count

def extGen(gen):
  work=[]
  for value in gen:
    work.append(value)
  return work

def findFillOrdersInBlock(block):
  for transaction in block['transactions']:
    for operation in transaction['operations']:
      if operation[0]==4:
        print(block['block_num'])

class DBDriver:
    #sql_map:
    __tables = {}

    __tables['p2pbridge_exchange_rates_meta'] = (
            "CREATE TABLE `p2pbridge_exchange_rates_meta` ("
        "`ID` INT(11) NOT NULL AUTO_INCREMENT,"
        "`SOURCE` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci',"
        "`BASE_ASSET_ID` INT(11),"
        "`QUOTE_ASSET_ID` INT(11),"
        "`ACTIVE` varchar(50) COLLATE utf8_unicode_ci DEFAULT 'N',"
        "PRIMARY KEY (`ID`))"
    "COLLATE='utf8_unicode_ci',"
    "ENGINE=InnoDB,"
    "AUTO_INCREMENT=27")

    __tables['p2pbridge_exchange_rates_values'] = (
            "CREATE TABLE `p2pbridge_exchange_rates_values` ("
        "`ID` INT(11) NOT NULL AUTO_INCREMENT,"
        "`RATE_ID` INT(11),"
        "`DATETIME` DATETIME NOT NULL,"
        "`VALUE` DOUBLE NOT NULL,"
        "`ACTIVE` varchar(1) COLLATE utf8_unicode_ci DEFAULT 'N',"
        "PRIMARY KEY (`ID`))"
    "COLLATE='utf8_unicode_ci',"
    "ENGINE=InnoDB,"
    "AUTO_INCREMENT=27")

    def __init__(self, sql_conf):
            # Set options
        self.__username = sql_conf['username']
        self.__password = sql_conf['password']
        self.__host = sql_conf['host']
        self.__database = sql_conf['database']
            # Database connect
        self.cnx = mysql.connector.connect(
            user = self.__username,
            password = self.__password,
            host = self.__host)
            # , database = self.__database
        self.cursor = self.cnx.cursor()
        self.__set_database()
        self.__create_table()

    def __getYamlSettings(self):
        pass

    def __set_database(self):
        try:
            self.cnx.database = self.__database
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.create_database(self.__database)
                self.cnx.database = self.__database
            else:
                print(err)
                exit(1)

    def __create_table(self):
        for name, ddl in self.__tables.items():
            try:
                print("Creating table {}: ".format(name), end='')
                self.cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

    def __create_database(self):
        try:
            self.cursor.execute("CREATE DATABASE {}"
                        "DEFAULT CHARACTER SET 'utf8'".format(self.__database))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)


'''
  "CREATE TABLE `courses` ("
  "  `id` int NOT NULL AUTO_INCREMENT,"
  "  `datetime` datetime NOT NULL,"
  "  `base` VARCHAR(255) NOT NULL,"
  "  `base_id` INT,"
  "  `base_amount` double NOT NULL,"
  "  `quote` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci',"
  "  `quote_id` INT,"
  "  `quote_amount` double NOT NULL,"
  "  `price` double NOT NULL,"
  "  PRIMARY KEY (`id`),"
  "  INDEX (base_id),"
  "  INDEX (quote_id),"
  "  FOREIGN KEY (base_id) REFERENCES p2pbridge_assets (id) ON DELETE RESTRICT ON UPDATE CASCADE,"
  "  FOREIGN KEY (quote_id) REFERENCES p2pbridge_assets (id) ON DELETE RESTRICT ON UPDATE CASCADE"
  ") ENGINE=InnoDB")
'''
#for block in extGen(test.blocks(1000000,1000100)):
    #print(block)
    #showOperationsInBlock(block)
#print(next(b))
#recprint(b)
#showOperationsInBlock(b)
