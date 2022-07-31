import sys
import math
import sqlite3


class Node:
    def __init__(self,data=None):
        self.data = data
        self.next = None
        self.prev = None

#Doubly Linked List
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

#Lets try to open the data base
conn = sqlite3.connect('MLData.db')
c = conn.cursor()

#Create table - Encryption
try:
    c.execute('''CREATE TABLE ENCRYPTION
             (data TEXT, timestamp FLOAT, entropy FLOAT,buffer_size INT)''')
except:
    print("Encryption Table is Already Active.")
try:
    c.execute('''CREATE TABLE NETWORK
                 (data TEXT, timestamp FLOAT, URL TEXT, malicious TEXT)''')
except:
    print("Network Table is Already Active.")

timeNow = 0
i = 0
while True:

    #Pull from the entries after our latest time stamp
    rows = c.execute('''SELECT entropy, timestamp FROM ENCRYPTION WHERE timestamp > '''+str(timeNow))

    Times = LinkedList()

    #We iterate over the time stamps
    for r in rows:
        newEntry = Node(r[1])
        timeNow = r[1]

        if i < 10:

            if Times.head is None:
                Times.head = newEntry
                Times.tail = newEntry
            else:
                Times.tail.next = newEntry
                newEntry.prev = Times.tail
                Times.tail = newEntry


    hold = Times.head
    while hold is not None and i < 5:
        print(hold.data)
        hold = hold.next
        i+=1
    #Iterate over the array and calculate average
