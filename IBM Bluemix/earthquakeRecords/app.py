from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import secure_filename
import ibm_db
import csv
import os
import math
from math import sin, cos, sqrt, atan2, radians


app = Flask(__name__)


ibmdb2cred = {
                #database credentials
}

db2conn = ibm_db.connect(
    "DATABASE=" + ibmdb2cred['db'] + ";HOSTNAME=" + ibmdb2cred['hostname'] + ";PORT=" + str(
        ibmdb2cred['port']) + ";UID=" +
    ibmdb2cred['username'] + ";PWD=" + ibmdb2cred['password'] + ";", "", "")


#home
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# search
@app.route('/searchbymagnitude')
def searchbymagnitude():
    return render_template('searchbymag.html')


@app.route('/searchresultmag', methods=['POST'])
def searchresultmag():
    if request.method == 'POST':
        result = request.form
        magnitude = float(result['mag'])
        sql = "SELECT * FROM earthquake where mag >= {}".format(magnitude)
        # print(sql)
        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        count = 0
        my_list = []
        while result:
            my_list.append([result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                            result['PLACE']])
            count += 1
            result = ibm_db.fetch_assoc(stmt)
        # print(my_list)
        # print(count)

        return render_template('searchresult.html', data=my_list, num=count)


#search by range(date and magnitude)
@app.route('/searchbyrange')
def searchbyrange():
    return render_template('searchbyrange.html')


@app.route('/magbyrange', methods=['POST'])
def magbyrange():
    if request.method == 'POST':
        result = request.form
        mag_low = float(result['starting'])
        mag_high = float(result['ending'])
        start = result['starting_date']
        end = result['ending_date']
        sql = "SELECT * FROM earthquake where mag BETWEEN {} and {}".format(mag_low, mag_high)
        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        count = 0
        my_list = []
        while result:
            time = result['TIME']
            date = time.split('.')
            date = date[0].split('T')
            date = str(date[0])
            if date >= start and date <= end:
                my_list.append([result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                                result['PLACE']])
                count += 1
            result = ibm_db.fetch_assoc(stmt)
        return render_template('searchresult.html', data=my_list, num=count)


#within a range
@app.route('/withinadistance')
def withinaplace():
    return render_template('withinadistance.html')


@app.route('/distanceresult', methods=['POST'])
def distanceresult():
    R = 6373.0  # radius of earth km
    if request.method == 'POST':
        result = request.form
        lat = result['lat']
        lon = result['lon']
        dist = float(result['dist'])
        sql = "SELECT * from earthquake"
        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        my_list = []
        count = 0
        while result:
            lat1 = radians(float(lat))
            lon1 = radians(float(lon))
            lat2 = radians(result['LATITUDE'])
            lon2 = radians(result['LONGITUDE'])

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c

            if distance <= dist:
                my_list.append([result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                                result['PLACE']])
                count += 1

            result = ibm_db.fetch_assoc(stmt)

        return render_template('searchresult.html', data=my_list, num=count)



@app.route('/searchclusters')
def searchclusters():
    return render_template('searchclusters.html')


@app.route('/grid', methods=['POST'])
def grid():
    if request.method == 'POST':
        result = request.form
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
        if lon1 >= lon2:
            max_lon = lon1
            min_lon = lon2
        else:
            max_lon = lon2
            min_lon = lon1

        sql = "SELECT * FROM earthquake WHERE latitude BETWEEN {} and {} and longitude BETWEEN {} and {}".format(
            min_lat, max_lat, min_lon, max_lon)

        stmt = ibm_db.exec_immediate(db2conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        rec_dict = dict()

        while result:
            if result['LATITUDE'] >= min_lat and result['LATITUDE'] <= max_lat:
                if result['LONGITUDE'] >= min_lon and result['LONGITUDE'] <= max_lon:
                    curr_lat = result['LATITUDE']
                    curr_lon = result['LONGITUDE']
                    target_lat = min_lat
                    target_lon = min_lon
                    while curr_lat >= target_lat:
                        target_lat += 1

                    while curr_lon >= target_lon:
                        target_lon += 1

                    if (target_lat, target_lon) in rec_dict:
                        rec_dict[(target_lat, target_lon)].append((curr_lat, curr_lon))
                    else:
                        rec_dict[(target_lat, target_lon)] = [(curr_lat, curr_lon)]

            result = ibm_db.fetch_assoc(stmt)

        return render_template('clusterresult.html', data=rec_dict.values())


@app.route('/daynight')
def daynight():
    sql = "SELECT * FROM earthquake"
    day_start = '06:00:00'
    day_end = '20:00:00'
    stmt = ibm_db.exec_immediate(db2conn, sql)
    result = ibm_db.fetch_assoc(stmt)
    my_list_day = []
    my_list_night = []
    count_night = 0
    count_day = 0
    high_mag_day = 0
    high_mag_night = 0
    while result:
        time = result['TIME']
        time = time.split('.')
        # print(time)
        time = time[0].split('T')
        # print(time)
        time = str(time[1])
        print(time)
        time = time.split(':')
        time = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
        lon = int(result['LONGITUDE'])

        if lon > 0:
            while lon != 0:
                time = time + 240
                lon -= 1

        elif lon < 0:
            while lon != 0:
                time = time - 240
                lon += 1

        hr = time // 3600
        # hr = hr // 24
        time = time - (hr * 3600)
        min = time // 60
        time = time - (min * 60)
        sec = time

        if hr < 0:
            hr = 24 + hr

        time = [str(hr), str(min), str(sec)]

        time = (':').join(time)
        print('new time', time)

        if result['MAG']:
            if time <= day_start or time >= day_end:
                my_list_night.append(
                    [result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                     result['PLACE']])
                count_night += 1

                if result['MAG'] > 4:
                    high_mag_night += 1

            else:
                my_list_day.append(
                    [result['TIME'], result['LATITUDE'], result['LONGITUDE'], result['DEPTH'], result['MAG'],
                     result['PLACE']])
                count_day += 1
                if result['MAG'] > 4:
                    high_mag_day += 1

        result = ibm_db.fetch_assoc(stmt)

    return render_template('resultdaynight.html', data_day=my_list_day, data_night=my_list_night, night=count_night, day=count_day,
                           high_day=high_mag_day, high_night=high_mag_night)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
    #app.run(debug=True)
