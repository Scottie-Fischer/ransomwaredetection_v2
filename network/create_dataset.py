import csv

#Append 1 to every entry to label data as malicios dns
dataset = []
with open('feed.txt', 'r') as malicious_dns_file:
    for entry in malicious_dns_file:
        dataset.append((entry))

#append 0 to every entry to label data as benign
with open('top-1m.csv') as benign_dns_file:
    parsed_file = csv.reader(benign_dns_file, delimiter=',')
    i=0
    for entry in parsed_file:
        if i==2500:
            break
        dataset.append("https://" + entry[1]+'\n')
        i+=1

#write out dataset to file
# with open('dataset_txt.csv', 'w') as output:
#     writer = csv.writer(output)
#     for entry in dataset:
#         writer.writerow(entry)

#write out dataset to text file
with open('url-list2.txt', 'w') as output:
    for entry in dataset:
        output.write(entry)
        

