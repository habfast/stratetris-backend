import csv
from classes import Connection, Train, Traffic, Demand
from fonctions import closest_connections, allocate_demand, compute_traffic
from connection_builder import connection_builder

def traffic_allocator(list_train1,capacity1,time_trajectory,demand1):

    del list_train1[:]

    """builds train list from csv"""

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
    
    list_connection1=connection_builder(list_train1,demand1.clients)
    list_connection1.sort(key=lambda connection: connection.schedule[connection.itinerary[-1],"arr"])
    
    print len(list_connection1)
    
    demand1.allocated=[0]
    
    compute_traffic(list_connection1,demand1,capacity1)
    
    for connection in list_connection1:
        print connection.schedule[connection.itinerary[-1],"arr"], connection.itinerary, connection.traffic
    
    for train in list_train1:
        print train.carrier, train.leg_occupancy
        '''if train.carrier!="TER":
            print train.carrier, train.leg_occupancy'''
    
    
def traffic_allocator_new_schedule(list_train1,capacity1,time_trajectory,demand1):
    
    for train in list_train1:
        train.traffic={}
        train.leg_occupancy={}
        train.available_OD={}
    demand1.allocated=[0]
    list_connection1=connection_builder(list_train1,demand1.clients)
    list_connection1.sort(key=lambda connection: connection.schedule[connection.itinerary[-1],"arr"])
    compute_traffic(list_connection1,demand1,capacity1)