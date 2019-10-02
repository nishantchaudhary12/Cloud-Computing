from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import secure_filename
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
import random


app = Flask(__name__)


server = ''
database = ''
username = ''
password = ''
driver=''
cnxn = pypyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()


R_SERVER  = redis.StrictRedis('#credentials')
TTL = 36



#home
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# @app.route('/searchmagnitude')
# def searchmagnitude():
#     return render_template('magnitude.html')


@app.route('/searchmagnitude')
def searchmag():
    result = request.form
    # mag_value = result['mag']
    my_list = list()
    count = 0
    start_time = time.time()

    # print(row)

    for each in range(1000):
        mag_value = random.randint(0, 8)
        cursor.execute("SELECT COUNT(*) FROM dbo.quakes$ WHERE mag > {}".format(mag_value))
        count += 1

        result = cursor.fetchone()

        row = list()
        while result:
            each = [str(i) for i in result]
            row.append(each)
            # row.append(result)
            result = cursor.fetchone()

        my_list.append(row)


    total_time = time.time() - start_time

    return render_template('searchresults.html', num=count, data=my_list, time=total_time)


# search
@app.route('/searchbymagnitude')
def searchbymagnitude():
    return render_template('searchbymagnitude.html')


@app.route('/searchbymag', methods=['POST'])
def searchbymag():
    if request.method == 'POST':
        result = request.form
        start = float(result['start'])
        # print(start)
        increment = 0.001
        stop = start + increment
        # print(stop)
        end = float(result['end'])
        # print(end)
        count = 0
        my_list = dict()
        start_time = time.time()
        while stop <= end:
            sql = "SELECT COUNT(*) FROM dbo.quakes$ WHERE mag BETWEEN {} AND {}".format(start, stop)
            hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
            key = "sql_cache:" + hash
            if (R_SERVER.get(key)):
                print("This was return from redis")
                row = cPickle.loads(R_SERVER.get(key))
            # print(start, stop)
            else:
                print('not redis')
                cursor.execute(sql)
                result = cursor.fetchone()
                # print(result)
                row = list()
                while result:
                    each = [str(i) for i in result]
                    row.append(each)
                    # row.append(result)
                    result = cursor.fetchone()
                if row:
                    save = list(row)
                else:
                    save = 0
                R_SERVER.set(key, cPickle.dumps(save))
            # print('1', result)
                # print('2', result)
            # print('here')
            # print(row)
            my_list[(start, stop)] = row

            count += 1
            start = stop
            stop += increment
            # print('yes')


        total_time = time.time() - start_time
        # print(my_list)
        return render_template('result.html', num=count, data=my_list.items(), time=total_time)



@app.route('/searchby', methods=['POST'])
def searchby():
    if request.method == 'POST':
        result = request.form
        start = float(result['start'])
        # print(start)
        increment = 0.001
        stop = start + increment
        # print(stop)
        end = float(result['end'])
        # print(end)
        count = 0
        my_list = {}
        start_time = time.time()
        while stop <= end:
            sql = "SELECT COUNT(*) FROM dbo.quakes$ WHERE mag BETWEEN {} AND {}".format(start, stop)
            print(start, stop)
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
            if result:
                my_list[(start, stop)] = result[0]
                count += result[0]
            # print('here')
            # count += 1
            start = stop
            stop += increment
            # print('yes')


        total_time = time.time() - start_time

        return render_template('new.html', data=my_list, time=total_time)




@app.route('/place')
def place():
    return render_template('place.html')


@app.route('/searchbyplace', methods=['POST'])
def searchplace():
    if request.method == 'POST':
        result = request.form
        place = result['Place']
        # print(sql)
        rows = []
        count = 0
        start_time = time.time()
        for i in range(1000):
            sql = "Select * from dbo.quakes$ WHERE place LIKE '%{}%' and mag BETWEEN 2 and 3".format(place)
            hash = hashlib.sha224(sql.encode('utf-8')).hexdigest()
            key = "sql_cache:" + hash
            if (R_SERVER.get(key)):
                print("This was return from redis")
                result = cPickle.loads(R_SERVER.get(key))
            # print(sql)
            else:
                cursor.execute(sql)
                row = cursor.fetchone()
                result = []
                while row:
                    row1 = [str(i) for i in row]
                    result.append(row1)
                    row = cursor.fetchone()
                # Put data into cache for 1 hour
                if result:
                    save = list(result)
                else:
                    save = 0
                R_SERVER.set(key, cPickle.dumps(save))

            print(result)
            rows.append(result)
                # cursor.execute(sql)
                # result = cursor.fetchone()
                # if result:
                #     my_list.append([result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'], result['PLACE']])
            count += 1

        total_time = time.time() - start_time

    return render_template('searchresults.html', num=count, data=rows, time=total_time)


@app.route('/viewbyrange')
def viewbyrange():
    return render_template('viewrange.html')


@app.route('/viewrange', methods=['POST'])
def rangeview():
    if request.method == 'POST':
        result = request.form
        # print(result)
        lat1 = float(result['lat1'])
        lat2 = float(result['lat2'])
        lon1 = float(result['lon1'])
        lon2 = float(result['lon2'])
        if lat1 >= lat2:
            max_lat = lat1
            min_lat = lat2
        else:
            max_lat = lat2
            min_lat = lat1
        # print(type(lon1))
        # print(type(lon2))
        # print(lon1 > lon2)
        if lon1 >= lon2:
            # print('yeah')
            max_lon = lon1
            min_lon = lon2
        else:
            # print('no')
            max_lon = lon2
            min_lon = lon1
        # print(min_lat, max_lat)
        # print(min_lon, max_lon)

        # print(sql)

        # print("Executed successfully!")

        # print(result)
        my_list = []
        count = 0
        start_time = time.time()
        for i in range(1000):
            sql = "SELECT * FROM dbo.quakes$ WHERE latitude BETWEEN {} and {} and longitude BETWEEN {} and {}".format(
                min_lat, max_lat, min_lon, max_lon)
            cursor.execute(sql)
            result = cursor.fetchone()
            my_list.append([result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                            result['PLACE']])
            count += 1
            # print(result)

        total_time = time.time() - start_time
        return render_template('searchresults.html', num=count, data=my_list, time=total_time)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=int(port))
    app.run()
    #app.run(debug=True)
