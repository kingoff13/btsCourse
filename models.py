import os
import yaml
import time
from sqlalchemy import Integer, Float, String, Boolean, DateTime, Column, Table
from sqlalchemy import create_engine, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('app.conf') as f:
    conf = yaml.safe_load(f.read())

sql_conf = conf.get('sql')
if not sql_conf:
    raise InvalidConfigurationError('SQL configuration missing')

engine_string = "mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}".format(
        **sql_conf)
engine = create_engine(engine_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class RateSource(Base):
    __tablename__ = 'p2pbridge_exchange_rates_source'
    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8_unicode_ci'))
    frequency = Column(Integer)


class RateValue(Base):
    __tablename__ = 'p2pbridge_exchange_rates_values'
    id = Column(Integer, primary_key=True)
    rate_id = Column(Integer)
    rate = relationship('Rate', foreign_keys=[rate_id], primaryjoin='Rate.id == RateValue.rate_id')
    datetime = Column(DateTime)
    value = Column(Float)
    active = Column(String(1, 'utf8_unicode_ci'), default='N')

    def __init__(self, rate_id, value):
        self.rate_id = rate_id
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        self.value = value
        self.active = 'Y'


class Rate(Base):
    __tablename__ = 'p2pbridge_exchange_rates_meta'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)
    source = relationship('RateSource', foreign_keys=[source_id], primaryjoin='RateSource.id == Rate.source_id')
    base_asset_id = Column(Integer)
    base_asset = relationship('Asset', foreign_keys=[base_asset_id], primaryjoin='Asset.id == Rate.base_asset_id')
    quote_asset_id = Column(Integer)
    quote_asset = relationship('Asset', foreign_keys=[quote_asset_id], primaryjoin='Asset.id == Rate.quote_asset_id')
    active = Column(String(1, 'utf8_unicode_ci'), default='N')


    def __repr__(self):
        return "<Rate('%s', '%s', '%s', '%s', '%s')" % (self.id, self.source, self.base_asset_id, self.quote_asset_id, self.active)


class Asset(Base):
    __tablename__ = 'p2pbridge_assets'
    id = Column(Integer, primary_key=True)
    asset_id = Column(String(255, 'utf8_unicode_ci'))
    symbol = Column(String(255, 'utf8_unicode_ci'))
    type_id = Column(Integer)
    market = Column(String(1, 'utf8_unicode_ci'))
    active = Column(String(1, 'utf8_unicode_ci'))
    issue = Column(String(255, 'utf8_unicode_ci'))
    precesion = Column(Integer)
    precision_deals = Column(Integer)
    precision_rates = Column(Integer)
    coinmarketcap_code = Column(String(255, 'utf8_unicode_ci'))
    max_market_fee = Column(String(255, 'utf8_unicode_ci'))
    max_supply = Column(String(255, 'utf8_unicode_ci'))
    description = Column(String(255, 'utf8_unicode_ci'))
    coinmarketcap_id = Column(Integer)
    monitor = Column(String(1, 'utf8_unicode_ci'))
    sort = Column(Integer)
    logo = Column(Integer)
    develop = Column(String(1, 'utf8_unicode_ci'))
    date_create = Column(DateTime)
    commission_in_transaction = Column(Float)
    commission_out_transaction = Column(Float)
    imf_name = Column(String(100, 'utf8_unicode_ci'))

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    session = Session()
    init_db()
