import random
import requests
import re
import os

base_url = "https://www.gutenberg.org/files/"
n_books = int(input('Enter the amount of books you want: '))
dir_path = os.getcwd() + '/gutenberg_books/'
pattern = "\"\d+-*\d*\.txt\""

if not os.path.exists(dir_path):
    os.makedirs(dir_path)

for i in range(n_books):
    book_url = base_url+str(random.randint(50000, 65000))
    r = requests.get(book_url)
    m = re.search(pattern, r.text)

    if not m:
        i-= 1
        continue
    
    file_name = m.group(0)[1:-1]
    file_url = book_url+"/"+file_name
    r = requests.get(file_url)

    if not r.ok:
        i -= 1
        continue

    open(dir_path+file_name, "wb").write(r.content)