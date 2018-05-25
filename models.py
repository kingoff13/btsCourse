import os
import yaml
from sqlalchemy import Integer, String, Boolean, DateTime, Column, Table
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

engine_string = "mysql+mysqlconnector://{username}:{password}@{host}:{port}/{db}".format(
        **sql_conf)
engine = create_engine(engine_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

