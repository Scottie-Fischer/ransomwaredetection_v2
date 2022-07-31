'''
Purpose: learn how to send thousands of requests asynchronously 
This code will query 100k websites asynchronously and print status of each connection
This code requires python3.7 or greater to work correctly
'''
from asyncio.tasks import create_task
import aiohttp
import asyncio
import asyncwhois
import csv
import time
from datetime import datetime, timezone
import math
import pandas as pd
import sqlite3
import pytz

async def get_status(session, url):
    # ensure that a thread will detach from a connection after 60 seconds, entire process is disconnect up to 150 seconds of runtime
    timeout = aiohttp.ClientTimeout(connect=10, total=30)
    # attempt to connect
    try:
        async with session.get(url, timeout=timeout) as response:
            res = [url, (response.status)]
            return [url,response.status]

    # could not connect to url
    except Exception as e:
        res = [url,404]
    return res
    
            
#create promises which are resolved when all requests are fulfilled. 
async def main(urls):
    # create a single session
    async with aiohttp.ClientSession() as session:

        tasks = []
        # send each request to parse_reqs and store the promise in tasks
        for url in urls:
            #tasks.append(asyncwhois.aio_lookup(url,10))
            tasks.append((get_status(session, url)))
        print('coroutines received, next resolve')

        # resolve the promises in tasks
        return await asyncio.gather(*tasks, return_exceptions=True)

#calculuate the number of days since the domain has been registered
def days_reg(whois_data):
    try:
        # datetime is not aware, pass date without timezone
        if whois_data['created'].tzinfo is None:
            today = datetime.now()
            diff = today - (whois_data['created'])
            diff = str(diff).split(' days')[0]
            return diff

        #datetime is aware, pass date with timezone
        elif whois_data['created'].tzinfo:
            today = datetime.now(pytz.utc)
            diff = today - (whois_data['created'])
            diff = str(diff).split(' days')[0]
            return diff
        
    #something went wrong
    except:
        return -1


#calculate the time for the domain to expire
def days_expire(whois_data):
    
    # datetime is not aware, pass date without timezone
    if whois_data['expires'].tzinfo is None:
        today = datetime.now()
        whois_data['expires']
        diff = today - (whois_data['expires'])
        diff = str(diff).split(' days')[0]
        return diff

    #datetime is aware, pass date with timezone
    elif whois_data['expires'].tzinfo:
        today = datetime.now(pytz.utc)
        diff = today - (whois_data['expires'])
        diff = str(diff).split(' days')[0]
        return diff 
    
    else:
        return -1
    
    

#calcaluate the shannon entropy of url
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

def num_subdomains(url):
    subdomains = url.split('http')[-1].split('//')[-1].split('/')
    return len(subdomains)-1

def domain_ext(url):
    ext = url.split('.')[-1].split('/')[0]
    return ext

urls = []
total_entries = 0
# parse entries and add only the urls to the urls array
with open('url-list2.txt') as list_urls:
    # parsed_file = csv.reader(benign_dns_file, delimiter=',')
    
    for entry in list_urls:
        if total_entries==2450:
            break
        entry = entry.rstrip("\n")
        urls.append(entry)
        total_entries+=1

# driver code, asynchronously receive website http status and whois daya
print('num urls' ,len(urls))
start_time = time.time()
total = asyncio.run(main(urls))
print("finished parsing network data")

# for each url, combine network and string based features and write to db
features = []
con = sqlite3.connect('features.db', isolation_level='DEFERRED')
cursor = con.cursor()
cursor.execute('''PRAGMA synchronous = OFF''')
cursor.execute('CREATE TABLE IF NOT EXISTS FEATURES(Url TEXT, HttpStatus INT, Registered INT, Expiration INT, Entropy INT, NumberDigits INT, UrlLength INT, NumParams INT, NumFragments INT, NumSubdomains INT, Extensions TEXT, Label INT)')
for i in range(0,len(total),2):
    whois_data = total[i]
    http_status = total[i+1][1]
    url = total[i+1][0]

    # if whois was unable to retrieve data, move on. Otherwise, add data to db
    if type(url) is not str or isinstance(whois_data, asyncwhois.errors.QueryError)\
         or isinstance(whois_data, asyncwhois.errors.NotFoundError) or isinstance(whois_data, asyncwhois.errors.WhoIsError):
        continue

    # retrieve all features and write to db
    else:
        try:
            dsr = days_reg(whois_data.parser_output)
        except:
            dsr = -1
        try:
            dse = days_expire(whois_data.parser_output)
        except:
            dse = -1
        en = entropy(url)
        if en is None:
            en = 0
        digits = num_digits(url)
        if digits is None:
            digits = 0
        url_length = url_len(url)
        if url_length is None:
            url_length = 0
        number_params = num_params(url)
        if number_params is None:
            number_params = 0
        num_frags = num_fragments(url)
        if num_frags is None:
            num_frags = 0
        subdomains = num_subdomains(url)
        if subdomains is None:
            subdomains = 0
        extns = domain_ext(url)
        if extns is None:
            extns = ''
        # 0 labels a good url, 1 labels a bad url
        label = 0
        if i>=2500:
            label=1

        cursor.execute('INSERT INTO FEATURES (Url, HttpStatus, Registered, Expiration, Entropy, NumberDigits, UrlLength, NumParams, NumFragments, NumSubdomains, Extensions, Label) values(?,?,?,?,?,?,?,?,?,?,?,?)', (url, http_status, dsr, dse, en, digits, url_length, number_params, num_frags, subdomains, extns, label))
        con.commit()

con.close()
duration = time.time() - start_time
print(f"Downloaded {len(total)} sites in {duration} seconds")