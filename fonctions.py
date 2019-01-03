def calculate_leg_occupancy(traffic_index,list_connection):
    """calculates traffic on each leg of each train in list_connection"""
    
    for train in [connection for connection in list_connection if connection.connecting_station=="direct"]:
        
        """initiates train leg list"""
        i=0
        while i<len(train.itinerary)-1:
            train.leg_occupancy[traffic_index,(train.itinerary[i],train.itinerary[i+1])]=0
            i+=1
        
        for connection in [connection for connection in list_connection if train in connection.connecting_trains]:

            """generates a list of OD from which traffic has to be allocated on train legs"""
            OD_list=[OD for (x,OD) in connection.traffic if x==traffic_index]

            """calculates occupancy on each leg"""
            for OD in OD_list:
                j=-1
                if set(OD).issubset(train.itinerary):
                    i=train.itinerary.index(OD[0])
                    j=train.itinerary.index(OD[1])
    
                elif connection.connecting_station!="direct" and set((OD[0],connection.connecting_station)).issubset(train.itinerary):
                    i=train.itinerary.index(OD[0])
                    j=train.itinerary.index(connection.connecting_station)
             
                elif connection.connecting_station!="direct" and set((connection.connecting_station,OD[1])).issubset(train.itinerary):
                    i=train.itinerary.index(connection.connecting_station)
                    j=train.itinerary.index(OD[1])
                
                if j>0:   
                    while i<j:
                        train.leg_occupancy[traffic_index,(train.itinerary[i],train.itinerary[i+1])]+=connection.traffic[traffic_index,OD]
                        i+=1  
    

def closest_connections(connection_list, OD, time, capacity, traffic_index):
    """Returns a list of the two available connections, that include OD, with closest departure time to time
    If time matches the exact departure time of a connection, this connection is returned twice in the list"""

    """filter trains that include OD, and removes trains with traffic over capacity"""    
    connection_list_available=[connection for connection in connection_list if set(OD).issubset(set(connection.itinerary)) and (traffic_index==0 or connection.available_OD[traffic_index-1, OD]) and connection.schedule[OD[0],"dep"]<connection.schedule[OD[1],"dep"]]

    train_number_list=[connection.connecting_trains[0].number for connection in connection_list_available if connection.connecting_station=="direct"]
    train_dep_list=[connection.schedule[OD[0],"dep"] for connection in connection_list_available if connection.connecting_station=="direct"]
    train_arr_list=[connection.schedule[OD[1],"arr"] for connection in connection_list_available if connection.connecting_station=="direct"]
    for connection in [connection1 for connection1 in connection_list_available if connection1.connecting_station!="direct"]:
        if connection.connecting_trains[0].number in train_number_list or connection.connecting_trains[1].number in train_number_list or connection.schedule[OD[0],"dep"] in train_dep_list or connection.schedule[OD[1],"arr"] in train_arr_list:
            connection_list_available.remove(connection)


    connection_list_available.sort(key=lambda connection: abs(connection.schedule[OD[0],"dep"]-time))
    return connection_list_available[:3]

def allocate_demand(list_connection,demand,traffic_index,capacity):
    """allocates demand on trains in list_train without any capacity constrain
    at each iteration, demand is split between the closest available trains
    the resulting traffic is added to train.traffic at a given index"""
    
    import math
    
    for OD in demand.clients:
        i=0
        while i<len(demand.clients[OD]):
            time=demand.init+i*demand.step
            list_closest_connections=closest_connections(list_connection, OD, time, capacity, traffic_index)
            total_utility=sum([math.exp((-(connection.schedule[OD[1],"arr"]-connection.schedule[OD[0],"dep"])*3-abs(time-connection.schedule[OD[0],"dep"])+connection.utility())/100) for connection in list_closest_connections])
            
            for connection in list_closest_connections:
                traffic_to_add=demand.clients[OD][i]*math.exp((-(connection.schedule[OD[1],"arr"]-connection.schedule[OD[0],"dep"])*3-abs(time-connection.schedule[OD[0],"dep"])+connection.utility())/100)/total_utility
                connection.traffic[traffic_index,OD]+=traffic_to_add
                
            i+=1

        

def compute_traffic(list_connection,demand,capacity):
    """allocates demand on trains in list_train with capacity constrain
    after each iteration, affected traffic & demand are reduced in ordrer to make the fullest train exactly 100% full
    this process is repeated as long as the allocated demand is not close enough to 1
    """
    ratio=[0]
    from classes import Demand
    
    list_train=[connection for connection in list_connection if connection.connecting_station=="direct"]
    
    for connection in list_connection:
        for OD in demand.clients:
            connection.traffic[0,OD]=0

    allocate_demand(list_connection, demand, 0, capacity)
    
    calculate_leg_occupancy(0,list_connection)
    
    for connection in list_connection:
        connection.calculate_available_OD([OD for OD in demand.clients],0,capacity)

    ratio[0]=1/max([train.peak_leg(0)*1.0/capacity[train.stock_type] for train in list_train])
    
    """test if no train is above capacity after first allocation"""
    if ratio[0]>=1:
        for connection in list_connection:
            for OD in demand.clients:
                connection.traffic[OD]=connection.traffic[0,OD]
                if connection.connecting_station!="direct":
                    connection.connecting_trains[0].traffic[OD]=connection.connecting_trains[0].traffic[0,OD]
                    connection.connecting_trains[1].traffic[OD]=connection.connecting_trains[0].traffic[0,OD]

        demand.allocated[0]=1
        
        print ratio[0], demand.allocated[0]
        
    else :
        
        """first iteration"""
        demand.allocated[0]=ratio[0]
        for connection in list_connection:
            for OD in demand.clients:
                connection.traffic[0,OD]=connection.traffic[0,OD]*ratio[0]

        print ratio[0], demand.allocated[0]

        """following iterations"""
        k=1
        while (ratio[k-1]-1)!=0:
            
            new_demand=Demand({},demand.init,demand.step,demand.allocated)
            for OD in demand.clients:
                new_demand.clients[OD]=[d-d*demand.allocated[k-1] for d in demand.clients[OD]]
            
            for connection in list_connection:
                for OD in demand.clients:
                    connection.traffic[k,OD]=connection.traffic[k-1,OD]
            
            allocate_demand(list_connection, new_demand, k, capacity)    
            ratio.append(0)
            demand.allocated.append(0)
            calculate_leg_occupancy(k,list_connection)

            ratio_list=[(train.peak_leg(k)-train.peak_leg(k-1))/(capacity[train.stock_type]-train.peak_leg(k-1)) for train in list_train if capacity[train.stock_type]!=train.peak_leg(k-1) and train.peak_leg(k)-train.peak_leg(k-1) and train.peak_leg(k)/capacity[train.stock_type]>=1]
            
            if len(ratio_list)!=0:
                ratio[k]=1/max(ratio_list)
                for connection in list_connection:
                    for OD in demand.clients:
                        connection.traffic[k,OD]=connection.traffic[k-1,OD]+ratio[k]*(connection.traffic[k,OD]-connection.traffic[k-1,OD])
            else:
                ratio[k]=1
            
            demand.allocated[k]=demand.allocated[k-1]+ratio[k]*(1-demand.allocated[k-1])
            calculate_leg_occupancy(k,list_connection)
            
            for connection in list_connection:
                connection.calculate_available_OD([OD for OD in demand.clients],k,capacity)
            
            print demand.allocated[k], ratio[k]
            k+=1
        
        for connection in list_connection:
            for OD in demand.clients:        
                connection.traffic[OD]=connection.traffic[k-1,OD]
                if connection.connecting_station!="direct":
                    connection.connecting_trains[0].traffic[OD]=connection.connecting_trains[0].traffic[k-1,OD]
                    connection.connecting_trains[1].traffic[OD]=connection.connecting_trains[1].traffic[k-1,OD]
                else:
                    i=0
                    while i<len(connection.itinerary)-1:
                        connection.leg_occupancy[connection.itinerary[i],connection.itinerary[i+1]]=connection.leg_occupancy[k-1,(connection.itinerary[i],connection.itinerary[i+1])]
                        i+=1
                        
    for connection in list_connection:
        
        """delete temporary traffic data used for iterations"""
        for OD in [OD for OD in connection.traffic if len(OD[1])!=3 or connection.traffic[OD]==0]:
            del connection.traffic[OD]
        if connection.connecting_station=="direct":
            for key in [key for key in connection.leg_occupancy if len(key[1])!=3]:
                del connection.leg_occupancy[key]
        