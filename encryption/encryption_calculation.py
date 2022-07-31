
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

def entropy_to_db(fileName, db_filename = 'maliciousness.db', read_times = 60, write_size = 4096, running_msg_flag = False):
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
    running_msg_flag : bool
        Flag to print a running message to know the program doesnt stall. (default False)
    """

    running_messages = ["Running |","Running /","Running -","Running \\"]
    running_message_index = 0
    running_messages_timer = time.time()


    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS ENCRYPTION(Time FLOAT, Entropy FLOAT)''')

    file_pos = 0  
    f = open(fileName,"rb+")
#     logf = open("log.txt", "w")
#     start = time.time() 

    while(True):
        # if((time.time() - start) > read_times):
        time.sleep(60)
        f.seek(file_pos)
        data = f.read()
#         start = time.time()
        entropy_arr = []
        last_minute_entropy = 0

        if(data == b''):
            continue

        chunks = [data[i:i+write_size] for i in range(0, len(data), write_size)]
        for byte_line in chunks:
            entropy_arr.append(entropy(byte_line))
        
        last_minute_entropy = sum(entropy_arr)/len(entropy_arr)
        file_pos = f.tell()

        c.execute("INSERT INTO ENCRYPTION (Time, Entropy) values (?,?)",
                (time.time(), last_minute_entropy))
        conn.commit()
    
        if(running_msg_flag and time.time() - running_messages_timer > .75):
            running_messages_timer = time.time()
            print('\r'+running_messages[running_message_index],end=' ')
            running_message_index = running_message_index + 1 if running_message_index < 3 else 0
    


if __name__ == "__main__":
    fileName = "data.txt"
    entropy_to_db(fileName, running_msg_flag = True)
