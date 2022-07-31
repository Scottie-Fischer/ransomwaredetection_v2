from requests import get
from os import listdir
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import seaborn as sns
import matplotlib.pyplot as plt
import math
from datetime import datetime
from pyquery import PyQuery
import sqlite3

# This creates a feature vector from a URL
class UrlFeaturizer(object):
    def __init__(self, url):
        self.url = url 
        self.domain = url.split('//')[-1].split('/')[0]
        self.today = datetime.now()
        
        # try:
        #     self.whois = whois.query(self.domain).__dict__
        # except:
        #     self.whois = None
        
        # try:
        #     self.response = get(self.url)
            
        # except:
        #     self.response = None
        
        # try:
        #     self.pq = PyQuery(self.response.text)
            
        # except:
        #     self.pq = None

            
    ## URL string Features
    def entropy(self):
        string = self.url.strip()
        prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
        entropy = sum([(p * math.log(p) / math.log(2.0)) for p in prob])
        return entropy
    
    def numDigits(self):
        digits = [i for i in self.url if i.isdigit()]
        return len(digits)
    
    def urlLength(self):
        return len(self.url)
    
    def numParameters(self):
        params = self.url.split('&')
        return len(params) - 1
    
    def numFragments(self):
        fragments = self.url.split('#')
        return len(fragments) - 1
    
    def numSubDomains(self):
        subdomains = self.url.split('http')[-1].split('//')[-1].split('/')
        return len(subdomains)-1
    
    def domainExtension(self):
        ext = self.url.split('.')[-1].split('/')[0]
        return ext
    
    ## URL domain features
    def hasHttp(self):
        return 'http:' in self.url 

    def hasHttps(self):
        return 'https:' in self.url 

    def urlIsLive(self):
        return self.response == 200
    
    def daysSinceRegistration(self):
        if self.whois and self.whois['creation_date']:
            diff = self.today - self.whois['creation_date']
            diff = str(diff).split(' days')[0]
            return diff
        else:
            return 0

    def daysSinceExpiration(self):
        if self.whois and self.whois['expiration_date']:
            diff = self.whois['expiration_date'] - self.today
            diff = str(diff).split(' days')[0]
            return diff
        else:
            return 0
    
    ## URL Page Features
    def bodyLength(self):
        print(self.pq)
        if self.pq is not None:
            return len(self.pq('html').text) if self.urlIsLive else 0
        else:
            return 0

    # def numTitles(self):
    #     if self.pq is not None:
    #         titles = ['h{}'.format(i) for i in range(7)]
    #         titles = [self.pq(i).items() for i in titles]
    #         return len([item for s in titles for item in s])
    #     else:
    #         return 0

    # def numImages(self):
    #     if self.pq is not None:
    #         return len([i for i in self.pq('img').items()])
    #     else:
    #         return 0

    # def numLinks(self):
    #     if self.pq is not None:
    #         return len([i for i in self.pq('a').items()])
    #     else:
    #         return 0
        
    # def scriptLength(self):
    #     if self.pq is not None:
    #         return len(self.pq('script').text())
    #     else:
    #         return 0
        
    # def specialCharacters(self):
    #     if self.pq is not None:
    #         bodyText = self.pq('html').text()
    #         schars = [i for i in bodyText if not i.isdigit() and not i.isalpha()]
    #         return len(schars)
    #     else:
    #         return 0
        
    # def scriptToSpecialCharsRatio(self):
    #     if self.pq is not None:
    #         sscr = self.scriptLength()/self.specialCharacters
    #     else:
    #         sscr = 0
    #     return sscr
    
    # def scriptTobodyRatio(self):
    #     if self.pq is not None:
    #         sbr = self.scriptLength()/self.bodyLength
    #     else:
    #         sbr = 0
    #     return sbr
    
    # def bodyToSpecialCharRatio(self):
    #     if self.pq is not None:
    #         bscr = self.specialCharacters()/self.bodyLength
    #     else:
    #         bscr = 0
    #     return bscr
        
    def run(self):
        data = {}
        data['domain'] = self.domain
        data['entropy'] = self.entropy()
        data['numDigits'] = self.numDigits()
        data['urlLength'] = self.urlLength()
        data['numParams'] = self.numParameters()
        # data['hasHttp'] = self.hasHttp()
        # data['hasHttps'] = self.hasHttps()
        # data['urlIsLive'] = self.urlIsLive()
        # data['bodyLength'] = self.bodyLength()
        # data['numTitles'] = self.numTitles()
        # data['numImages'] = self.numImages()
        # data['numLinks'] = self.numLinks()
        # data['scriptLength'] = self.scriptLength()
        # data['specialChars'] = self.specialCharacters()
        # data['ext'] = self.domainExtension()
        # data['dsr'] = self.daysSinceRegistration()
        # data['dse'] = self.daysSinceExpiration()
        # data['sscr'] = self.scriptToSpecialCharsRatio()
        # data['sbr'] = self.scriptTobodyRatio()
        # data['bscr'] = self.bodyToSpecialCharRatio()
        return data


#Driver code
con = sqlite3.connect('classify_urls.db')
df = pd.DataFrame()
dataset = []
with open("url-list.txt",'r') as urls:
    for url in urls:
        res = UrlFeaturizer(url).run()
        dataset.append(res)
        
df = pd.DataFrame(dataset)
df.to_sql('features', con)
#df.to_csv('features.csv')