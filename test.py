#!python

import csv
from classes import Connection, Train, Traffic, Demand
from fonctions import closest_connections, allocate_demand, compute_traffic
from connection_builder import connection_builder


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



capacity1={}
capacity1['D']=510
capacity1['DD']=1020
capacity1['Q']=350
capacity1['B']=340

"""builds train list from csv"""
list_train1=[]
with open('SA2020_JOB_2_sens.csv', mode='r') as csv_file:
    data = csv.DictReader(csv_file, delimiter=';') 
    for x in data:
        origin_time=int(x['dep_time'].split(':')[0])*60+int(x['dep_time'].split(':')[1])
        iti=tuple(x['itinerary'].split('-'))
        sched={}
        k=0
        for station in iti:
            sched[station,"arr"]=origin_time+time_trajectory[iti][k]
            sched[station,"dep"]=origin_time+time_trajectory[iti][k+1]
            k+=2
        list_train1.append(Train(x['carrier'],x['number'],sched,{},x['stock_type'],iti))

    

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
        

list_connection1=connection_builder(list_train1,demand1.clients)
list_connection1.sort(key=lambda connection: connection.schedule[connection.itinerary[-1],"arr"])

print len(list_connection1)

compute_traffic(list_connection1,demand1,capacity1)

for connection in list_connection1:
    print connection.schedule[connection.itinerary[-1],"arr"], connection.itinerary, connection.traffic

for train in list_train1:
    print train.carrier, train.leg_occupancy
    '''if train.carrier!="TER":
        print train.carrier, train.leg_occupancy'''

with open("output_file.csv", mode="w") as output_file:
    fieldnames=["carrier","train_number","OD_dep","OD_arr","train_dep_time","train_arr_time","OD_dep_time","OD_arr_time","OD_connecting_station","connection_traffic"]
    writer=csv.DictWriter(output_file,fieldnames=fieldnames,delimiter=";")
    writer.writeheader()
    for connection in list_connection1:
        for OD in [OD for OD in connection.traffic if set(OD).issubset(set(connection.itinerary))]:
            OD_dep_time_minutes = connection.schedule[(OD[0],"dep")]
            OD_dep_time = "{}:{}".format(OD_dep_time_minutes//60, OD_dep_time_minutes%60)
            OD_arr_time_minutes = connection.schedule[(OD[1],"arr")]
            OD_arr_time = "{}:{}".format(OD_arr_time_minutes//60, OD_arr_time_minutes%60)
            OD_connecting_station = connection.connecting_station
            for train in connection.connecting_trains:
                if connection.traffic[OD]!=0:
                    train_dep_time_minutes = train.schedule[(train.itinerary[0],"dep")]
                    train_dep_time = "{}:{}".format(train_dep_time_minutes//60, train_dep_time_minutes%60)
                    train_arr_time_minutes = train.schedule[(train.itinerary[-1],"arr")]
                    train_arr_time = "{}:{}".format(train_arr_time_minutes//60, train_arr_time_minutes%60)
                    writer.writerow({"carrier":train.carrier,"train_number":train.number,"OD_dep":OD[0],"OD_arr":OD[1],"train_dep_time":train_dep_time,"train_arr_time":train_arr_time,"OD_dep_time":OD_dep_time,"OD_arr_time":OD_arr_time,"OD_connecting_station":OD_connecting_station,"connection_traffic":connection.traffic[OD]})
                    
                    
                    
                    