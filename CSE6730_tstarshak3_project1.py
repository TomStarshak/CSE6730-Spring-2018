# -*- coding: utf-8 -*-
"""
CSE 6730: Modeling and Simulation
Project 1
"""

import numpy as np

#constants:
mean_arrival_time = 15
closing_time = 480
mean_party_size = 4
sd_party_size = 2
min_party_size = 1
min_cook_time = 15
max_cook_time = 60
min_meal_time = 45
max_meal_time = 120


# The Future Event List is a linked list a tuples where each tuple consists of:
# 1 - The timestamp of the event
# 2 - The entity on which the event acts
# 3 - The type of event that occurs
#The simulation begins when the first party arrives, so the first event is set
class node:
   def __init__(self):
     self.data = None
     self.next = None
 
class linked_list:
   def __init__(self):
     self.head = None

#search through the list to find the correct position to add the given event   
   def add_node(self, data):
     current = self.head
     #if the list is empty, just add node
     if current is None:
       temp = node()
       temp.data = data
       self.head = temp
       return
     #if the first node is > than the node to be added, add node at the beginning
     if current.data > data:
       temp = node()
       temp.data = data
       temp.next = current
       self.head = temp
       return
     
    #move through the list until the node to be added is greater than the previous node in the list
     while current.next is not None:
       if current.next.data > data:
         break
       current = current.next
     temp = node()
     temp.data = data
     temp.next = current.next
     current.next = temp
     return

#remove the first element of the FEL from the list     
   def remove_head(self):
     current = self.head
     if current.next == None:
         self.head = None
     else:
         current.data = current.next.data
         current.next = current.next.next
         
#read the data from the first element in the FEL     
   def head_info(self):
     current = self.head
     if current == None:
         return None
     else:
         return current.data
        
#print methods for troubleshooting help
   def __str__(self):
     data = []
     curr = self.head
     while curr is not None:
       data.append(curr.data)
       curr = curr.next
     return "[%s]" %(', '.join(str(i) for i in data))
   
   def __repr__(self):
     return self.__str__()

#initialize FEL 
FEL = linked_list()
FEL.add_node((0,'party1','arrive'))


# Dictionary containing all parties that have arrived at the restaurant
# Parties will be represented by a list with elements [arrival time, size of party, has_ordered, has_eaten, has_paid, wait_time, leave time]
parties = {}

#Set the initial state of the server
server = 'idle'
busy_until = 0
    
    

def party_arrive(name, time):
    """takes in the name of a party and the arrival time of that party
    Caclulates the size of the party
    Updates the parties dictionary
    Schedules the arrival of the subsequent party if there is time before the restaurant closes
    """
    size = int(max(min_party_size, np.rint(np.random.normal(mean_party_size, sd_party_size))))
    parties[name] = [time, size, False, False, False, 0, 0]
    
    #calculate when the next party should arrive
    next_arrival_time = time + int(max(1, np.random.poisson(mean_arrival_time)))
    
    #if the next party would arrive before the restaurant closes, add them to the future event list
    if (next_arrival_time < closing_time):
        FEL.add_node((next_arrival_time, 'party' + str(len(parties) + 1), 'arrive'))
        
    
    #remove the first event from the Future Event List        
    FEL.remove_head()
    
    #schedule the ordering event
    FEL.add_node((time, name, 'order'))
    
        
        
    
def party_order(name, time):
    """
    Begins the ordering process for the party 'name' at time 'time'
    Updates the state of the server to 'busy'
    Calculates the cooking time of the order as the max of the individual cook times for each meal
    Schedules the end of the order as well as the serve time
    """
    global server
    global busy_until
    #time to finish order
    order_time = parties[name][1]
    
    #update server states
    server = 'busy'
    busy_until = time + order_time
    
    #update party state
    parties[name][2] = True
    
    #remove the first event from the Future Event List        
    FEL.remove_head()
    
    #calculate cook time = maximum of the cook time of the individual meals
    cook_time = 0
    for i in range(parties[name][1]):
        cook_time = max(cook_time, np.random.randint(min_cook_time, max_cook_time))

    
    #schedule end of order
    FEL.add_node((time + order_time, name, 'end_order'))
        
    #schedule food serving
    FEL.add_node((time + cook_time, name, 'serve_food'))
    
    
def end_order(name, time):
    """
    Ends the order
    Sets the server to 'idle'
    """
    global server
    global busy_until
    server = 'idle'
    busy_until = time
    
    FEL.remove_head()
    
def serve_food(name, time):
    """
    Event where the food is served.
    Sets the server to busy for the duration.
    Schedules the end of service event.
    """
    global server
    global busy_until
    #time to serve the food = size of party
    serve_time = parties[name][1]
    
    #update server states
    server = 'busy'
    busy_until = time + serve_time
    
    #schedule end of service
    FEL.add_node((time + serve_time, name, 'end_service'))
    
    FEL.remove_head()
    
def end_service(name, time):
    """
    Event that signals the end of service.
    Sets server state to idle.
    Calculates the length of the meal.
    Schedules the end of the meal.
    """
    global server
    global busy_until
    
    #update server state
    server = 'idle'
    busy_until = time
    
    #calculate meal length = random time between min and max meal time        
    meal_length = np.random.randint(min_meal_time, max_meal_time)
    
    #schedule end of meal
    FEL.add_node((time + meal_length, name, 'pay_for_meal'))
    
    FEL.remove_head()
    
def pay_for_meal(name, time):
    """
    Event that simulates the bill being paid
    Sets the server to 'busy' for the duration.
    Schedules the end of payment
    """
    global server
    global busy_until
    
    #time to ring up bill = size of party
    time_to_pay = parties[name][1]
    
    #update server states
    server = 'busy'
    busy_until = time + time_to_pay
    
    #update party state 
    parties[name][3] = True
    
    #schedule end of payment
    FEL.add_node((time + time_to_pay, name, 'finish_pay'))
    
    FEL.remove_head()
    
def finish_pay(name, time):
    """
    Event that simulates the end of bill payment.
    Sets the server state to 'idle'
    """
    global server
    global busy_until
    
    #update server states
    server = 'idle'
    busy_until = time
    
    #update party state
    parties[name][4] = True
    parties[name][6] = time
    
    FEL.remove_head()
    
    
#main simulation loop
while FEL.head_info():
    #choose the first event in the FEL
    event = FEL.head_info()[2]
    
    if event == 'arrive':
        party_arrive(FEL.head_info()[1], FEL.head_info()[0])
        
    elif event == 'order':
        if server == 'idle':
            party_order(FEL.head_info()[1], FEL.head_info()[0])
        #reschedule order until server is free    
        else:
            parties[FEL.head_info()[1]][5] += (busy_until + 1 - FEL.head_info()[0])
            FEL.add_node((busy_until + 1, FEL.head_info()[1], 'order' ))            
            FEL.remove_head()
            
    elif event == 'end_order':
        end_order(FEL.head_info()[1], FEL.head_info()[0])
        
    elif event == 'serve_food':
        if server == 'idle':
            serve_food(FEL.head_info()[1], FEL.head_info()[0])
        #reschedule serving food until server is free
        else:
            parties[FEL.head_info()[1]][5] += (busy_until + 1 - FEL.head_info()[0])
            FEL.add_node((busy_until + 1, FEL.head_info()[1], 'serve_food'))
            FEL.remove_head()
            
    elif event == 'end_service':
        end_service(FEL.head_info()[1], FEL.head_info()[0])
        
    elif event == 'pay_for_meal':
        if server == 'idle':
            pay_for_meal(FEL.head_info()[1], FEL.head_info()[0])
        #reschedule payment
        else:
            parties[FEL.head_info()[1]][5] += (busy_until + 1 - FEL.head_info()[0])
            FEL.add_node((busy_until + 1, FEL.head_info()[1], 'pay_for_meal'))
            FEL.remove_head()
    else:
        finish_pay(FEL.head_info()[1], FEL.head_info()[0])
  
leave_time = 0
paying_customers = 0
for key in parties:
    print('Party '+key[5:]+' spent %i minutes in the restaurant and had to wait %i minutes total for service.' % (parties[key][6] - parties[key][0], parties[key][5]))
    if parties[key][6] > leave_time:
        leave_time = parties[key][6]
    if parties[key][5]/(parties[key][6] - parties[key][0]) < 0.25:
        paying_customers += 1
print('Total time = %i   mins.'% leave_time)
print('Total paying customers = %i'% paying_customers)
