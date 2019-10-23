import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.account import Account

account = Account(init_amount=100000,start_date='20190101')
account.df.to_excel('test_account.xlsx')

