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

    else :
        
        """first iteration"""
        demand.allocated[0]=ratio[0]
        for connection in list_connection:
            for OD in demand.clients:
                connection.traffic[1,OD]=connection.traffic[0,OD]*demand.allocated[0]
                if connection.connecting_station!="direct":
                    connection.connecting_trains[0].traffic[1,OD]=connection.connecting_trains[0].traffic[0,OD]*demand.allocated[0]
                    connection.connecting_trains[1].traffic[1,OD]=connection.connecting_trains[1].traffic[0,OD]*demand.allocated[0]
                
        new_demand=Demand({},demand.init,demand.step,demand.allocated)
        for OD in demand.clients:
            new_demand.clients[OD]=[d-d*demand.allocated[0] for d in demand.clients[OD]]
        allocate_demand(list_connection, new_demand, 1, capacity)
    
        for connection in list_connection:
            connection.calculate_available_OD([OD for OD in demand.clients],1,capacity)
    
        """following iterations"""
        k=1
        while (ratio[k-1]-1)!=0:
            ratio.append(0)
            demand.allocated.append(0)
            ratio[k]=1/max([(train.peak_leg(k)-train.peak_leg(k-1)*demand.allocated[k-1])/(capacity[train.stock_type]-train.peak_leg(k-1)*demand.allocated[k-1]) for train in list_train if capacity[train.stock_type]!=train.peak_leg(k-1)*demand.allocated[k-1] and train.peak_leg(k)/capacity[train.stock_type]>1])
            
            '''for train in list_train:
                if (train.peak_leg(k)!=train.peak_leg(k-1)*demand.allocated[k-1]):
                    if ratio[k]==(capacity[train.stock_type]-train.peak_leg(k-1)*demand.allocated[k-1])/(train.peak_leg(k)-train.peak_leg(k-1)*demand.allocated[k-1]):
                        print "ITERATION", k, train.number, train.peak_leg(k), train.peak_leg(k-1)*demand.allocated[k-1]

            for train in list_train:
                if train.peak_leg(k)==340:
                    print "ITERATION", k, train.number, train.peak_leg(k), train.peak_leg(k-1)*demand.allocated[k-1]'''
            
            """print "TO max", max([train.peak_leg(k)/capacity[train.stock_type] for train in list_train])"""
            
            demand.allocated[k]=demand.allocated[k-1]+ratio[k]*(1-demand.allocated[k-1])
            for connection in list_connection:
                for OD in demand.clients:
                    connection.traffic[k+1,OD]=connection.traffic[k-1,OD]*demand.allocated[k-1]+ratio[k]*(connection.traffic[k,OD]-connection.traffic[k-1,OD]*demand.allocated[k-1])
                    if connection.connecting_station!="direct":
                        connection.connecting_trains[0].traffic[k+1,OD]=connection.connecting_trains[0].traffic[k-1,OD]*demand.allocated[k-1]+ratio[k]*(connection.connecting_trains[0].traffic[k,OD]-connection.connecting_trains[0].traffic[k-1,OD]*demand.allocated[k-1])
                        connection.connecting_trains[1].traffic[k+1,OD]=connection.connecting_trains[1].traffic[k-1,OD]*demand.allocated[k-1]+ratio[k]*(connection.connecting_trains[1].traffic[k,OD]-connection.connecting_trains[1].traffic[k-1,OD]*demand.allocated[k-1])

            new_demand=Demand({},demand.init,demand.step,demand.allocated)
            for OD in demand.clients:
                new_demand.clients[OD]=[d-d*demand.allocated[k] for d in demand.clients[OD]]

            
            allocate_demand(list_connection, new_demand, k+1, capacity)
            

            '''for train in list_train:
                if (train.peak_leg(k)!=train.peak_leg(k-1)*demand.allocated[k-1]):
                    if ratio[k]==(capacity[train.stock_type]-train.peak_leg(k-1)*demand.allocated[k-1])/(train.peak_leg(k)-train.peak_leg(k-1)*demand.allocated[k-1]):
                        print train.number, train.peak_leg(k+1)            '''
            
            
            for connection in list_connection:
                connection.calculate_available_OD([OD for OD in demand.clients],k+1,capacity)
            
            print demand.allocated[k], ratio[k]
            k+=1
        
        for connection in list_connection:
            for OD in demand.clients:        
                connection.traffic[OD]=connection.traffic[k,OD]
                if connection.connecting_station!="direct":
                    connection.connecting_trains[0].traffic[OD]=connection.connecting_trains[0].traffic[k,OD]
                    connection.connecting_trains[1].traffic[OD]=connection.connecting_trains[1].traffic[k,OD]
    
    for connection in list_connection:
        
        """delete temporary traffic data used for iterations"""
        for OD in [OD for OD in connection.traffic if len(OD[1])!=3 or connection.traffic[OD]==0]:
            del connection.traffic[OD]
        
        """remove connecting traffic from direct OD-trains"""
        if connection.connecting_station!="direct":
            for OD in [OD for OD in connection.traffic if len(OD[1])==3 and connection.traffic[OD]!=0]:
                if (OD[0],connection.connecting_station) in connection.connecting_trains[0].traffic:
                    connection.connecting_trains[0].traffic[(OD[0],connection.connecting_station)]+=-connection.traffic[OD]
                if (connection.connecting_station,OD[1]) in connection.connecting_trains[1].traffic:
                    connection.connecting_trains[1].traffic[(connection.connecting_station,OD[1])]+=-connection.traffic[OD]