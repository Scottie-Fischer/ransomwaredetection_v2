import collections
import math
import sys
import os
import time
import pandas as pd
from scipy import stats
import sqlite3

def entropy(data):
    pd_series = pd.Series(list(data))
    counts = pd_series.value_counts()
    return stats.entropy(counts, base=2)

def entropy_to_db(fileName, db_filename = 'MLData.db', read_times = 60, write_size = 4096):
    """
    Parameters
    ----------
    fileName : str
        The name of the file to continuously read from
    db_filename : str
        The name of the .db file to write to
    read_times : int, optional
        Interval at which it reads and calculates the entropy in seconds. (default is 60)
        Might want to have an big enough window to have accurate readings and might want to have it match window_size.
    write_size : int, optional
        Size of writes in the drive (default is 4096, 4KB)
    """
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

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
    
    file_pos = 0  
    f = open(fileName,"rb+")
    logf = open("log.txt", "w")
    start = time.time() 

    while(True):
        if((time.time() - start) > read_times):
            f.seek(file_pos)
            data = f.read()
            start = time.time()
            entropy_arr = []
            last_minute_entropy = 0

            if(data == b''):
                continue

            chunks = [data[i:i+write_size] for i in range(0, len(data), write_size)]
            for byte_line in chunks:
                entropy_arr.append(entropy(byte_line))
            
            last_minute_entropy = sum(entropy_arr)/len(entropy_arr)
            file_pos = f.tell()

            c.execute("INSERT INTO ENCRYPTION (data, timestamp, entropy, buffer_size) values (?,?,?,4)",
                    (data, time.time(), last_minute_entropy))
            conn.commit()


def entropy_sliding_window(fileName, window_size = 60, sub_window_size = 15, treshold = 5.5, write_size = 4096, read_times = 60):
    """
    Parameters
    ----------
    fileName : str
        The name of the file to continuously read from
    window_size : int, optional
        The size of the desired sliding window (default is 60)
    sub_window_size: int, optional
        The size of the sub window to check for clusters of high entropy against treshold (default is 15)
    treshold : int, optional
        Upper bound for the entropy of clusters to raise the alarm (default is 5.5)
    write_size : int, optional
        Size of writes in the drive (default is 4096, 4KB)
    read_times : int, optional
        Interval at which it reads and calculates the entropy in seconds. (default is 60)
        Might want to have an big enough window to have accurate readings and might want to have it match window_size.
    """
    running_messages = ["Running |","Running /","Running -","Running \\"]
    running_message_index = 0
    running_messages_timer = time.time()

    window = [0 for i in range(window_size)]
    file_pos = 0
    ndx = 0
    
    try:
        assert(sub_window_size < window_size)
    except AssertionError:
        print('sub_window_size cannot be bigger than window_size')
        
    f = open(fileName,"rb+")
    logf = open("log.txt", "w")
    start = time.time()
    while(True):
        if((time.time() - start) > read_times):
            f.seek(file_pos)

            data = f.read()
            start = time.time()
            entropy_arr=[]

            if(data == b''):
                continue

            chunks = [data[i:i+write_size] for i in range(0, len(data), write_size)]
            if(len(chunks) == 0):
                print(data)
            for byte_line in chunks:
                entropy_arr.append(entropy(byte_line))
            
            window[ndx] = sum(entropy_arr)/len(entropy_arr)
            
            file_pos = f.tell()
            ndx+=1
            if(ndx<sub_window_size):
                sub_window = window[ndx-sub_window_size::]+ window[:ndx]
            else:
                sub_window = window[ndx-sub_window_size:ndx]
            ave = sum(sub_window)/sub_window_size
            logf.write(f'Average{ave} \n for the values {sub_window}\n and a total window {window}\n--------------\n\n')

            if(ave>treshold):
                print(time.strftime("%H:%M:%S",time.localtime()))
                print('An attack might be occuring')
            
            if(ndx>59):
                ndx = 0
        if(time.time() - running_messages_timer > .75):
            running_messages_timer = time.time()
            print('\r'+running_messages[running_message_index],end=' ')
            running_message_index = running_message_index + 1 if running_message_index < 3 else 0
    

if __name__ == "__main__":
    fileName = "data.txt"
    entropy_to_db(fileName)
    entropy_sliding_window(fileName,read_times=60)

