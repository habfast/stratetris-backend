class Connection:

    def __init__(self,sched,traf,iti,trains,station):
        self.schedule=sched
        self.traffic={}
        self.itinerary=iti
        self.connecting_trains=trains
        self.connecting_station=station
        self.available_OD={}


    def utility(self):
        
        if self.connecting_station!="direct":
            return -30
        else:
            return 0
    
    
    def calculate_available_OD(self, OD_test_list, traffic_index, capacity):

        for test_OD in OD_test_list:
            
            """this case if connection has only one train with one leg"""
            if len(self.itinerary)==2:
                if test_OD==self.itinerary:
                    self.available_OD[traffic_index,test_OD] = self.traffic[traffic_index,self.itinerary]<capacity[self.connecting_trains[0].stock_type]
                else:
                    self.available_OD[traffic_index,test_OD] = False

            """test if all legs are available on OD"""
            available=1
            if set(test_OD).issubset(set(self.itinerary)) and self.schedule[test_OD[0],"dep"]<self.schedule[test_OD[1],"dep"]:
                
                i=self.itinerary.index(test_OD[0])
                j=self.itinerary.index(test_OD[1])
                
                """if connection is direct"""
                if self.connecting_station=="direct":
                    while i<j:
                        available*=(self.connecting_trains[0].leg_occupancy[traffic_index,(self.itinerary[i],self.itinerary[i+1])]<capacity[self.connecting_trains[0].stock_type])
                        i+=1
                    
                    """if connection has more than 1 train"""
                else:
                    k=self.itinerary.index(self.connecting_station)
                    while i<k:
                        available*=(self.connecting_trains[0].leg_occupancy[traffic_index,(self.itinerary[i],self.itinerary[i+1])]<capacity[self.connecting_trains[0].stock_type])
                        i+=1
                    while i<j:
                        available*=(self.connecting_trains[1].leg_occupancy[traffic_index,(self.itinerary[i],self.itinerary[i+1])]<capacity[self.connecting_trains[1].stock_type])
                        i+=1
                
                if available==1:
                    self.available_OD[traffic_index,test_OD] = True
                else:
                    self.available_OD[traffic_index,test_OD] = False
            else:
                self.available_OD[traffic_index,test_OD] = False


class Train(Connection):
    
    def __init__(self,carr,num,sched,traf,stock,iti):
        self.carrier=carr
        self.number=num
        self.leg_occupancy={}
        self.stock_type=stock


        Connection.__init__(self,sched,traf,iti,[self],"direct")
        
    def peak_leg(self, traffic_index):
        """returns train's fullest leg"""
        return max([self.leg_occupancy[key] for key in self.leg_occupancy if key[0]==traffic_index])


class Traffic:
    
    def __init__(self,list_traffic_OD):
        self.traffic=list_traffic_OD

class Demand:
    
    def __init__(self,cli,i,s,all):
        self.clients=cli
        self.init=i
        self.step=s
        self.allocated=all