'''
Retrieve URL's from user specified file
Extract features from URL and write to dataframe
Pass features to ML model and record output in maliciousness DB
'''

from datetime import datetime
import requests
import math
import time
import pandas as pd
import pickle
import sqlite3

def get_site_status(url):
    status_code = -1
    try:
        response = requests.head(url, timeout=10)
        status_code = response.status_code
    except Exception as e:
        status_code = 404
    return status_code

def entropy(url):
    string = url.strip()
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    entropy = sum([(p * math.log(p) / math.log(2.0)) for p in prob])
    return entropy
    
def num_digits(url):
    digits = [i for i in url if i.isdigit()]
    return len(digits)

def url_len(url):
    return len(url)

def num_params(url):
    params = url.split('&')
    return len(params) - 1

def num_fragments(url):
    fragments = url.split('#')
    return len(fragments) - 1

def check_db_for_malicious_conn(db_filename = '../maliciousness.db', window_size = 15):
    c = sqlite3.connect(db_filename)
    cur = c.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS PREDICTIONS(Prediction TEXT, Time FLOAT)')
    cur.execute('''SELECT Prediction,Time FROM PREDICTIONS''')
    rows = cur.fetchall()
    for r in rows[-window_size::]:
        if r[0] == "1":
            return True
    return False

#Driver code
def main(fileName = 'net_data.txt', db_fileName = '../maliciousness.db', model_fileName = 'model.pkl'):
    con = sqlite3.connect(db_fileName)
    cursor = con.cursor()    
    net_traffic = open(fileName, "r+")

    #import ml model from file
    ml_model = None
    with open(model_fileName, 'rb') as file:
        ml_model = pickle.load(file)


    while(True):
        pos = net_traffic.tell()
        url = net_traffic.readline()
        if(url == ""):
            net_traffic.seek(pos)
            time.sleep(20)
            continue

        url = url.rstrip("\n")

        # extrac features from URL
        status = get_site_status(url)
        entropy_val = entropy(url)
        digits = num_digits(url)
        length = url_len(url)
        params = num_params(url)
        frags = num_fragments(url)
        features_dict = {
            "Entropy": entropy_val,
            "UrlLength": length,
            "HttpStatus": status,
            "NumberDigits": digits,
            "NumberParams": params,
            "NumFragments": frags
        }

        # write features to dataframe
        df = pd.DataFrame(features_dict, index=[0])

        # use df to predict maliciousness of url
        prediction = ml_model.predict(df)[0]

        now = datetime.now()
        date_time =time.time()
        cursor.execute('CREATE TABLE IF NOT EXISTS PREDICTIONS(Prediction TEXT, Time FLOAT)')
        cursor.execute('INSERT INTO PREDICTIONS(Prediction, Time) values(?,?)', (str(prediction), date_time))
        con.commit()
        
    con.close()


if __name__ == "__main__":
    print(check_db_for_malicious_conn())
    main()