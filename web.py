#!/usr/bin/python

from flask import Flask, request, Response
from classes import Connection, Train, Traffic, Demand
import requests
import json
import csv
from run_traffic_allocator import traffic_allocator, traffic_allocator_new_schedule

list_train1=[]

capacity1={}
capacity1['D']=510
capacity1['DD']=1020
capacity1['Q']=350
capacity1['B']=350

time_trajectory={}
time_trajectory[("LLE","PNO")]=(0,0,61,61)
time_trajectory[("LLE","QRV","PNO")]=(0,0,20,25,80,80)
time_trajectory[("ADI","HZK","XBH","XLE","QRV","PNO")]=(0,0,20,23,43,46,57,60,74,88,133,133)
time_trajectory[("ADI","LLE","QRV","PNO")]=(0,0,31,51,72,77,128,128)
time_trajectory[("AEB","STH","LLE","QRV","PNO")]=(0,0,21,31,60,76,97,102,153,153)
time_trajectory[("XVS","XDN","QRV","PNO")]=(0,0,25,36,50,62,113,113)
time_trajectory[("XVS","LLE")]=(0,0,30,30)
time_trajectory[("ADI","HZK","XBH","XLE","QRV")]=(0,0,30,32,61,63,79,81,93,93)
time_trajectory[("XDN","QRV")]=(0,0,13,13)
time_trajectory[("XDN","VTY","QRV")]=(0,0,11,12,26,26)
time_trajectory[("ADI","LLE")]=(0,0,31,31)
time_trajectory[("ADI","LLE","QRV","AMS")]=(0,0,31,51,72,77,108,108)
time_trajectory[("AEB","STH","LLE")]=(0,0,21,31,60,60)
time_trajectory[("STH","LLE")]=(0,0,29,29)
time_trajectory[("PNO","LLE")]=(0,0,62,62)
time_trajectory[("PNO","QRV","LLE")]=(0,0,49,55,76,76)
time_trajectory[("PNO","QRV","XLE","XBH","HZK","ADI")]=(0,0,49,53,66,70,82,86,107,110,133,133)
time_trajectory[("PNO","QRV","LLE","ADI")]=(0,0,49,55,76,88,118,118)
time_trajectory[("PNO","QRV","LLE","STH","AEB")]=(0,0,49,55,76,93,121,132,153,153)
time_trajectory[("PNO","QRV","XDN","XVS")]=(0,0,49,53,67,78,103,103)
    
"""imports demand from csv"""
demand1=Demand({},300,10,[0])
with open('Demande_Ma_2017_10min_2_sens.csv', mode='r') as csv_file:
    data = csv.DictReader(csv_file, delimiter=';') 
    for demand_per_time in data:
        OD=tuple(demand_per_time["OD"].split('-'))
        k=0
        demand1.clients[OD]=[]
        while k<len(demand_per_time)-1:
            demand1.clients[OD].append(int(demand_per_time[str(demand1.init+k*demand1.step)]))
            k+=1


app = Flask(__name__)

@app.route('/api/run_traffic_allocator/')
def traffic_allocator_api():
    traffic_allocator(list_train1,capacity1,time_trajectory,demand1)
    return Response("")

@app.route('/api/all_stations/')
def get_all_stations_api():
    list_stations=["AEB","STH","ADI","LLE","HZK","XBH","XLE","XVS","XDN","QRV","PNO"]
    return Response(json.dumps(list_stations))

@app.route('/api/train_list/')
def get_train_list_api():
    list_train_simplified = []
    for train in list_train1:
        train_simplified={}
        train_simplified["carrier"]=train.carrier
        train_simplified["number"]=train.number
        train_simplified["capacity"]=capacity1[train.stock_type]
        train_simplified["itinerary"]=train.itinerary
        train_simplified["leg_occupancy"]={key[0]+"-"+key[1] : train.leg_occupancy[key] for key in train.leg_occupancy}
        train_simplified["schedule"]={key[0]+"-"+key[1] : train.schedule[key] for key in train.schedule}
        list_train_simplified.append(train_simplified)
        
    return Response(json.dumps(list_train_simplified))

@app.route('/api/rerun_allocator_new_schedule/', methods = ['POST'])
def rerun_allocator_new_schedule_api():
    new_time_origins = request.get_json
    print(new_time_origins)
    for train in list_train1:
        if train.number in new_time_origins:
            new_schedule={}
            k=0
            origin_time=new_time_origins[train.number]
            for station in train.itinerary:
                new_schedule[station,"arr"]=origin_time+time_trajectory[train.itinerary][k]
                new_schedule[station,"dep"]=origin_time+time_trajectory[train.itinerary][k+1]
                k+=2
            train.schedule=new_schedule
    traffic_allocator_new_schedule(list_train1,capacity1,time_trajectory,demand1)
    return Response("")

@app.route('/', methods=['POST', 'GET'], defaults={'path': ''})
@app.route('/<path:path>')

def _proxy(*args, **kwargs):
    
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, 'http://localhost:8080/'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
