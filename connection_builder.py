
def connection_builder(train_list, OD_list):
    
    connection_list=[]

    from classes import Connection

    """builds all possible connections"""
    
    for OD in OD_list:
    
        for train1 in train_list:
            if set([OD[0]]).issubset(set(train1.itinerary)):
                if set([OD[1]]).issubset(set(train1.itinerary)):
                    connection_list.append(train1)
                i=train1.itinerary.index(OD[0])
                for train2 in train_list:
                    if train1!=train2 and set([OD[1]]).issubset(set(train2.itinerary)):
                        j=train2.itinerary.index(OD[1])
                        for station in train1.itinerary:
                            if train1.itinerary.index(station)>i and set([station]).issubset(set(train2.itinerary)) and train2.itinerary.index(station)<j and train1.schedule[station,"arr"]+10<train2.schedule[station,"dep"]:
                                new_schedule={}
                                new_itinerary=train1.itinerary[i:train1.itinerary.index(station)+1]+train2.itinerary[train2.itinerary.index(station)+1:j+1]
                                for sched_station in new_itinerary:
                                    if new_itinerary.index(sched_station)<new_itinerary.index(station):
                                        new_schedule[sched_station,"arr"]=train1.schedule[sched_station,"arr"]
                                        new_schedule[sched_station,"dep"]=train1.schedule[sched_station,"dep"]
                                    elif new_itinerary.index(sched_station)>new_itinerary.index(station):
                                        new_schedule[sched_station,"arr"]=train2.schedule[sched_station,"arr"]
                                        new_schedule[sched_station,"dep"]=train2.schedule[sched_station,"dep"]
                                    else:
                                        new_schedule[sched_station,"arr"]=train1.schedule[sched_station,"arr"]
                                        new_schedule[sched_station,"dep"]=train2.schedule[sched_station,"dep"]
                                connection_list.append(Connection(new_schedule,{},new_itinerary,(train1,train2),station))
    
    """removes connections if a faster connection exists with same dep or arr times"""
    for connection1 in connection_list:
        for connection2 in [connection for connection in connection_list]:
            if set(connection2.itinerary).issubset(connection1.itinerary) and connection1!=connection2 and (connection2.connecting_station!="direct" or connection1.connecting_station=="direct" and connection2.connecting_station=="direct"):
                if connection1.schedule[connection2.itinerary[0],"dep"]==connection2.schedule[connection2.itinerary[0],"dep"] and connection1.schedule[connection2.itinerary[-1],"arr"]<=connection2.schedule[connection2.itinerary[-1],"arr"]:
                    connection_list.remove(connection2)
                elif connection1.schedule[connection2.itinerary[-1],"arr"]==connection2.schedule[connection2.itinerary[-1],"arr"] and connection1.schedule[connection2.itinerary[0],"dep"]>=connection2.schedule[connection2.itinerary[0],"dep"]:
                    connection_list.remove(connection2) 
    
    for train in train_list:
        connection_list.append(train)
    return list(set(connection_list))
