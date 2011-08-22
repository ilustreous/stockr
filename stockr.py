# -*- coding: utf-8 -*-
"""
    STOCKR
    ~~~~~~~~

    Let's view some stock data from yahoo

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement
import time
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash

import json
import pprint
import MySQLdb as sql
import MySQLdb.cursors as cursors

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('STOCKR_SETTINGS', silent=True)

pp = pprint.PrettyPrinter(indent=4)

def _query(query):

    db = sql.connect(user="root",passwd="root", db="stockr")
    cursor = db.cursor()
    
    try:
           cursor.execute(query)
           
           while(1):
               row = cursor.fetchone()
               if row == None:
                   break
               yield row

    finally:
        db.close()
        cursor.close()
        
@app.route('/symbol/<sym>')
def symbol(sym):
    query = """select * 
                 from historical_prices 
                where symbol = \'%(sym)s\' order by date""" % vars()

    query_handler = _query(query)

    ds = [(d[0], d[-1]) for d in query_handler]
    
    ds_json = json.dumps(ds)

    return render_template('symbols.html', data=ds, symbol=sym,
            data_json=ds_json)

@app.route('/')
def index():

    query = """select symbol, count(1) 
                 from stockr.historical_prices 
                group by symbol 
                order by symbol"""
    query_handler = _query(query)
    
    ds = [q for q in query_handler]
    
    return render_template('index.html', datasetlen=len(ds), data=ds)


if __name__ == '__main__':
    app.run(port=8000, debug=True, use_reloader=False)
