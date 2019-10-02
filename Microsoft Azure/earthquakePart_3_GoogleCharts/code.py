from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import secure_filename
import random
import csv
import os
import math
from math import sin, cos, sqrt, atan2, radians
import time
import redis
import pypyodbc
import hashlib
import _pickle as cPickle
import datetime


app = Flask(__name__)


server = ''
database = ''
username = ''
password = ''
driver=''
cnxn = pypyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# chaudhary.redis.cache.windows.net:6380,password=EdUJDQoNdOiGTauBcLRm6LwI6kjjdj1b5cSg5d+arK4=,ssl=True,abortConnect=False
R_SERVER  = redis.StrictRedis(host='', port=6380, db=0, password='', ssl=True)
TTL = 36


#home
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


#magnitude range
@app.route('/magrange')
def magrange():
    return render_template('magnituderange.html')


@app.route('/searchbymagnitude', methods=['POST'])
def searchbymagnitude():
    if request.method == 'POST':
        result = request.form
        start = float(result['start'])
        end = float(result['end'])
        increment = 0.1
        stop = start + increment
        my_dict = dict()
        while stop <= end:
            sql = "SELECT COUNT(*) FROM dbo.quake6 WHERE mag BETWEEN {} AND {}".format(start, stop)
            cursor.execute(sql)
            result = cursor.fetchone()
            # print(result)

            my_dict[(start, stop)] = result[0]

            start = float(format(stop, '.2f'))
            # stop = start + increment
            stop = float(format(stop + increment, '.2f'))

        print(my_dict)

        return render_template('magnituderangeresult.html', data=my_dict.items())



if __name__ == "__main__":
    app.run()
    #app.run(debug=True)


