from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import secure_filename
import csv
import os
import math
import pypyodbc
from sklearn.cluster import KMeans
import time
from flaskext.mysql import MySQL
import redis
from redis import Redis
import hashlib
import _pickle as cPickle
from flask import session
from flask_session import Session
import datetime


application = Flask(__name__)
app = application

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = ''

mysql.init_app(app)

conn = mysql.connect()

cursor = conn.cursor()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/cluster')
def cluster():
    return render_template('cluster.html')


@app.route('/clusterresult', methods=['POST'])
def clusterresult():
    if request.method == 'POST':
        result = request.form
        k = int(result['clust'])
        sql = "SELECT fare, age From titanic3 WHERE fare != {} and age != {}".format(0, 0)
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        data = list()
        while result:
            data.append((result[0], result[1]))
            result = cursor.fetchone()

        flag = True
        x_cor = list()  # stores x coord
        y_cor = list()  # y coor
        dist = list()  # distance

        for each in range(k):
            x_cor.append(data[each][0])
            y_cor.append(data[each][1])

        for num in range(k):  # initialized with zero to avoid out of index error, we have that many indexes we need
            dist.append(0)

        while flag:
            clusters = dict()  # dict to store key value pairs, key being the mean at that point
            for num in range(len(x_cor)):
                clusters[
                    (x_cor[num], y_cor[num])] = []  # dict with a key which represents the cluster points at that points

            for each in data:  # iterations for dataset
                for num in range(len(x_cor)):  # iterations checking data for distance with each cluster
                    d = math.sqrt(((x_cor[num] - each[0]) ** 2) + ((y_cor[num] - each[1]) ** 2))
                    dist[num] = float(
                        format(d, '.2f'))  # dist list, data from first cluster at 0 index and from second at 1 index
                indx = dist.index(min(dist))  # minimum distance from cluster
                clusters[(x_cor[indx], y_cor[indx])].append(
                    each)  # coordinate added to the key in dictionary based on which cluster it is nearer to

            cluster_points = list()  # get the value for all the keys so that we can operate on them
            for each in clusters:
                cluster_points.append(clusters[each])

            new_cor_x = list()  # for storing the new coordinates of cluster
            new_cor_y = list()

            for each in cluster_points:
                x_dim = 0
                y_dim = 0

                for num in range(len(each)):  # calculating the mean of x and y coordinates
                    x_dim += each[num][0]
                    y_dim += each[num][1]

                new_cor_x.append(x_dim / len(each))  # will store the new coordinates of x and y
                new_cor_y.append(y_dim / len(each))

            distance_new = list()  # will store the distance between old cluster point and the new ones

            for each in range(len(x_cor)):
                d = math.sqrt(((new_cor_x[each] - x_cor[each]) ** 2) + ((new_cor_y[each] - y_cor[each]) ** 2))
                distance_new.append(d)

            diff = math.sqrt(sum(
                distance_new))  # the distance between the old cluster and new clusters is added for all clusters and then square root for error calculation

            if diff == 0:
                flag = False

            else:
                x_cor = new_cor_x
                y_cor = new_cor_y

        print('Clusters')
        for num in range(len(x_cor)):
            print(clusters[x_cor[num], y_cor[num]])

        print('Cluster points')
        for each in clusters.keys():
            print(each)

    return render_template('clusterresult.html', data=clusters.items())


@app.route('/clusters')
def clusters():
    return render_template('clusters.html')


@app.route('/clustersresult', methods=['POST'])
def clustersresult():
    print('yes')
    if request.method == 'POST':
        print('here')
        result = request.form
        xaxis = result['xaxis']
        yaxis = result['yaxis']
        k = int(result['kclusters'])
        sql = "SELECT " + result['xaxis'] + "," + result['yaxis'] + " FROM titanic3 WHERE " + result[
            'xaxis'] + " != 0 and " + result['yaxis'] + " != 0;"
        print(sql)
        cursor.execute(sql)

        row = cursor.fetchone()
        result = []
        X = []
        while row:
            row = list(row)
            X.append(row)
            row = cursor.fetchone()

        kmeans = KMeans(n_clusters=k).fit(X)
        centroids = kmeans.cluster_centers_

        print(centroids)
        kmeans_transform = kmeans._transform(X).tolist()
        point_distance = []
        clusters = [[] for i in range(k)]
        print(X)
        for i in range(len(X)):
            c_index = kmeans_transform[i].index(min(kmeans_transform[i]))
            clusters[c_index].append(X[i])
            temp = {"point": X[i], "distance_from_centroid": kmeans_transform[i]}
            point_distance.append(temp)


        print(clusters)
        print(temp)
        for each in clusters:
            print(len(each))
        spread = list()
        for each in range(len(clusters)):
            dist_list = list()
            for pair in clusters[each]:
                # print(centroids[each][0], centroids[each][1])
                d = math.sqrt(((centroids[each][0] - pair[0]) ** 2) + ((centroids[each][1] - pair[1]) ** 2))
                dist_list.append(d)

            dist = max(dist_list)
            spread.append(dist)
            print(spread)

        return render_template('clustersresult.html', centroids=centroids, clusters=clusters)


@app.route('/population')
def population():
    global year
    global col
    if year < 2019:
        pop_list = list()
        print(pop_list)
        start_time = datetime.datetime.now()
        start = time.time()
        sql = "SELECT {} from population where State = 'Texas'".format(col)
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
        if result:
           pop_list.append(result)
        # cursor.close()
        print(pop_list)
        sql = "SELECT {} from population where State = 'Louisiana'".format(col)
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
        if result:
            pop_list.append(result)
        # cursor.close()
        print(pop_list)
        sql = "SELECT {} from population where State = 'Oklahoma'".format(col)
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
        if result:
            pop_list.append(result)
        # cursor.close()

        year += 1
        col = chr(ord(col) + 1)
        print(year)
        print(col)
        end_time = datetime.datetime.now()
        end = time.time() - start
    else:
        year = 2010
        col = 'a'
    print(pop_list)

    return render_template('population.html', data=pop_list, start=start_time, end=end_time, total=end)


@app.route('/bonus')
def bonus():
    return render_template('bonus.html')

@app.route('/bonusresult', methods=['POST'])
def bonusresult():
    if request.method == 'POST':
        result = request.form
        count = 0
        global year
        global col
        num = int(result['num'])
        start_time = time.time()
        time_elapsed = 0
        time_request = list()
        while time_elapsed <= num:
            start = time.time()
            if year < 2019:
                pop_list = list()
                # print(pop_list)
                # start_time = datetime.datetime.now()

                sql = "SELECT {} from population where State = 'Texas'".format(col)
                # print(sql)
                cursor.execute(sql)
                result = cursor.fetchone()
                # print(result)
                if result:
                    pop_list.append(result)
                # cursor.close()
                # print(pop_list)
                sql = "SELECT {} from population where State = 'Louisiana'".format(col)
                # print(sql)
                cursor.execute(sql)
                result = cursor.fetchone()
                # print(result)
                if result:
                    pop_list.append(result)
                # cursor.close()
                # print(pop_list)
                sql = "SELECT {} from population where State = 'Oklahoma'".format(col)
                # print(sql)
                cursor.execute(sql)
                result = cursor.fetchone()
                # print(result)
                if result:
                    pop_list.append(result)
                # cursor.close()

                year += 1
                col = chr(ord(col) + 1)
                # print(year)
                # print(col)
                # end_time = datetime.datetime.now()

            else:
                year = 2010
                col = 'a'
            end = time.time() - start
            time_request.append(end)
            # print(pop_list)
            count += 1
            curr_time = time.time()
            time_elapsed = curr_time - start_time
            # print(time_elapsed)
            print(count)
            print(time_request)
        return render_template('bonusresult.html', count=count, time_request=time_request)



if __name__ == '__main__':
    app.run()
