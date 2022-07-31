# Network detection
## List of features extracted
- Days registered
- Days until expired
- Website reachability (HTTP status)
- url entropy
- number of digits
- length of the url
- number of parameters
- number of fragments
- number of subdomains
- domain extension(s) (if any)

## Week of 04/26
Whois is such a pain. So many different errors you gotta check. Just finished whois and should provide only relevant information

## Week of 4/19
Spent a LOT of time working on [async.py](async.py)  Am now able to successfully query 100k domains in under 2 minutes. 2 days
Figured out the features I want to pass to the ML model:\
entropy, numdigits, urllength, numparameters, numfragments, numubdomains, domainextension, urlislivem, dayssinceregistartiondayssinceexpiration\
After reviewing papers, found that we must determine the whois data for the creation and expiration date, we must find entropy, check if domain is live, and splicing url is a useful feature as well.\
Next must classify each url and add appropriate feature to sqlite DB as chosen by the team. 

Finished classifying non-internet based features. Added those to classify_urls.db

## Added requirements.txt
I exported the requirements in my conda env to a requirements.txt file. To create a new env with the correct requirements, please execute:
`conda create --name <env> --file requirements.txt`

## What I did for the week of 4/12
More data preprocessing. Made sure all url's were queryable. This work can be found in create_dataset.py\
[Based of off this article](https://towardsdatascience.com/predicting-the-maliciousness-of-urls-24e12067be5), wrote a script to extract features from URLs. A few of the libraries were outdated so I found new ones and updated the code accordingly. 

## Major Issue

When the class is instantiated, sending each get request takes a couple of seconds. We have over 700k of websites which need to be queried and classified.
This will take days to do. About half of the features which can be extracted from the url are contigent on receieving a response back from the domain. Here are my proposed solutions:
1. Figure out how to increase the speed of the network calls (multithreading?) done
2. ~~Use only the features which do not require a network call and try and build an ML model off of those~~
3. ~~[Use the data provided in the study but they only have ~500 entries](https://github.com/eneyi/dataarchive/blob/master/pmurls/data/scanned_data.csv
)~~
