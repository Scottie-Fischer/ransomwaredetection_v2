import sys
import math
import sqlite3
import time

class Node:
    def __init__(self,data=None,time=None):
        self.data = data
        self.time = time
        self.next = None
        self.prev = None


#Doubly Linked List
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None


# Lets try to open the data base
conn = sqlite3.connect('../maliciousness.db')
c = conn.cursor()

# Create table - Encryption
try:
    c.execute('''CREATE TABLE ENCRYPTION
             (Time FLOAT, Entropy FLOAT)''')
except:
    print("Encryption Table is Already Active.")
try:
    c.execute('''CREATE TABLE NETWORK
                 (Time FLOAT, Prediction TEXT)''')
except:
    print("Network Table is Already Active.")

timeNow = 1622566343.0 #time.time()    # This is the time of the last entry
i = 0
sigE_count = 0
sigN_count = 0
windowE = LinkedList()
windowN = LinkedList()

while True:
    #If already a head pop off and move window
    if windowN.head is not None:

        if windowN.head.next is not None:
            #Decrease Alert Signal Count if applicable
            temp = windowN.head
            if temp.data == 1:
                sigN_count -= 1
            #Pop off head thus moving the window
            windowN.head = windowN.head.next
            timeNow = windowN

        #If our window is empty we just move the time 1 second ahead
        else:
            windowN.head = None
            timeNow += 1
    elif timeNow != 0:
        timeNow += 1

    #we want to sync both the windows together
    if windowE.head is not None:
        #Sync encryption window with our network window
        while windowE.head.time < timeNow:
            if windowE.head.next is None:
                windowE.head = None
                break
            else:
                if windowE.head.data >= 5.5:
                    sigE_count -=1
                windowE.head = windowE.head.next

    # Now that both windows are moved and synced we want to pull entries that we will add to our window
    # Pull from the entries after our latest time stamp and within the window range (1 minute)
    rowE = c.execute('''SELECT Entropy, Time FROM ENCRYPTION WHERE Time < ''' + str(timeNow + 10289.558) + " AND Time < " + str(timeNow+10289.558-600))
    rowN = c.execute('''SELECT Prediction, Time FROM NETWORK WHERE Time < ''' + str(timeNow) + " AND Time < " + str(timeNow - 600))


    # We iterate over the new entries and add to our counters and linked lists
    for r in rowE:
        #Make a Node for our entry
        newEntry = Node(r[1],r[0])

        #Add this entry to our window linked list
        if windowE.tail is not None:
            windowE.tail.next = newEntry
            windowE.tail = newEntry
        else:
            windowE.tail = newEntry
        #If parameters are met increment counter of signal
        if newEntry.data > 5.3:
            sigE_count += 1

    for r in rowN:
        newEntryN = Node(r[0],r[1])
        if windowN.tail is not None:
            windowN.tail.next = newEntryN
            windowN.tail = newEntryN
        else:
            windowN.tail = newEntryN

        if newEntryN.time > 1622500000.0:
            print("newEntry at : " + str(newEntryN.time) + " with value: " + newEntryN.data)
        if newEntryN.data == '1':
            sigN_count += 1

    #Now that our window is created check if two signals exist in the window
    if sigE_count > 0 and sigN_count > 0:
        print("Attack Detected")
    #elif sigE_count > 0:
        #print("entropy high at time:" + str(timeNow))
    #elif sigN_count > 0:
        #print("Malicious traffic at time: ")
    else:
        i += 1
        if (i % 50000) == 0:
            print("Activity Normal at time:" + str(timeNow))
        #print("Activity Normal at time:" + str(timeNow))
