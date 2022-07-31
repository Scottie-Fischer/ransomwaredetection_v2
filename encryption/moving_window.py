import ransomware_detection

import sqlite3
import time

def moving_window(dbFileName, window_in_sec , network_flag, threshold = 5.5, bias = 0, ):
    
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ENCRYPTION(Time FLOAT, Entropy FLOAT)''')

    while(True):
        
        rows = c.execute('''SELECT Entropy, Time FROM ENCRYPTION WHERE Time > ''' + str(time.time() - window_in_sec))
        entropyAve = 0
        count = 0
        for r in rows.fetchall():
            entropyAve += r[0]
            count+=1
        
        if(count != 0):
            entropyAve = entropyAve/count

        #TODO: Need to retrieve and set bias in DB for seasonality
        
        if(entropyAve > threshold + bias):
            ransomware_detection.entropy_alert(network_flag.is_set())
        
        time.sleep(60)

if __name__ == "__main__":
    moving_window('../MLData.db', 900)