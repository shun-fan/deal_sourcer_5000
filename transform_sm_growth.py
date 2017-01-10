#! /usr/bin/python

# transform Second measure raw to growth
# ACloudGuru,https://acloud.guru/,2015-10-01,491
# this template
# http://stackoverflow.com/questions/31394998/using-sqlalchemy-to-load-csv-file-into-a-database
# how to make a string column
# http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables
import csv
import ConfigParser
import traceback
import re
from time import time
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, Float, DateTime, String, BigInteger, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sp_util import format_string, format_number, format_date
from load_sm_csv import SmMonthlyRevenue

Base = declarative_base()

class CompanyGrowth(Base):
    __tablename__ = 'growth'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255))
    domain = Column(String(255))
    one_month = Column(Float())
    three_month = Column(Float())
    six_month = Column(Float())
    twelve_month = Column(Float())
    last_revenue = Column(Float())
    # one month ago
    one = Column(Integer)
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)
    ten = Column(Integer)
    eleven = Column(Integer)
    twelve = Column(Integer)
    __table_args__ = (Index('name', 'name'), Index('last', 'last_revenue'))

def build_object(name, domain, sales, growth, last):
    return CompanyGrowth(**{
        'name':name,
        'domain':domain,
        'one_month':growth[0],
        'three_month':growth[1],
        'six_month':growth[2],
        'twelve_month':growth[3],
        'one':sales[0],
        'two':sales[1],
        'three':sales[2],
        'four':sales[3],
        'five':sales[4],
        'six':sales[5],
        'seven':sales[6],
        'eight':sales[7],
        'nine':sales[8],
        'ten':sales[9],
        'eleven':sales[10],
        'twelve':sales[11],
        'last_revenue':last
    })

def calculate_growth(months, sales):
    """Input sales and months, output 1, 3, 6, 12 month growth, if it exists.
    Input should be ordered in reverse chronological order and indicies should
    correspond.

    Input should all begin on the same month. If there is a data set with a 0,
    return 0 for all subsequent growth numbers.
    """
    end = len(months)
    growth = [0, 0, 0, 0]
    milestones = [0, 3, 6, 10]
    g_sum = 0;
    for i in range(11):
        if (sales[i] == 0 or sales[i+1] == 0):
            break
        else:
            g_sum += ((sales[i] - sales[i+1]) / float(sales[i+1])) * 100
        if i in milestones:
            growth[milestones.index(i)] = format(g_sum / float(i+1), '.0f')
    return growth

def transform_to_sm_growth(engine):
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    for company in s.query(SmMonthlyRevenue.name).distinct():
        #print str(company[0])
        months = []
        sales = []
        name = company[0]
        domain = ''
        for x in reversed(s.query(SmMonthlyRevenue)
                .filter_by(name=company[0])
                .all()):
            #print x.name, x.month, x.observed_sales
            months.append(x.month)
            sales.append(x.observed_sales)
            domain = x.domain


        growth = calculate_growth(months=months, sales=sales)
        record = build_object(name=name, domain=domain, sales=sales,
                              growth=growth, last=sales[0])
        s.add(record)

    try:
        s.commit()
    except:
        s.rollback() #Rollback the changes on error
        print 'Unexpected error on index ' \
            + str(i) + ':' + traceback.format_exc()

if __name__ == "__main__":
    t = time()

    #Create the database
    print 'connecting to mysql database'
    engine = create_engine('mysql://root@127.0.0.1/test3?charset=utf8mb4')
    Base.metadata.create_all(engine)

    transform_to_sm_growth(engine=engine)