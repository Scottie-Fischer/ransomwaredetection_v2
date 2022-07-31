#Send GET and POST requests to every URL in dataset

import requests

#send POST to each domain in feed.txt
with open('feed.txt', 'r') as malicious_dns_file:
    for domain in malicious_dns_file:
        #send post
        try:
            response = requests.post(domain)
            print("Domain: ", domain, "POST status code: ", response.status_code)
            response = requests.get(domain)
            print("Domain: ", domain, "GET status code: ", response.status_code)
        except:
            print("could not connect to URL")