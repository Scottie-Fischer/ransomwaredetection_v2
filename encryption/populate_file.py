import random
import requests
import re
import pyAesCrypt
import io
import time

def get_gut_file():
    base_url = "https://www.gutenberg.org/files/"
    pattern = "\"\d+-*\d*\.txt\""

    book_url = base_url+str(random.randint(50000, 65000))
    r = requests.get(book_url)
    m = re.search(pattern, r.text)
    if not m:
        return("ERR")
        
    file_url = book_url+"/"+m.group(0)[1:-1]
    r = requests.get(file_url)
    if not r.ok:
        return("ERR")
    
    return(r.content)

def get_data_helper():
    try:
        data = get_gut_file()
        while(data == "ERR"):
            data = get_gut_file()
    except:
        data = ""
        
    return data

def encrypt_data(data, size, password):
    dat = io.BytesIO(data)
    ciph = io.BytesIO()
    pyAesCrypt.encryptStream(dat, ciph, password, size)
    return(ciph.getvalue())


def write_file(attack = False, writes_size = 4, filename = 'data.txt'):
    modes = ["normal", "mixed", "encryption"]
    writes_size *= 1024
    password = "password"
    
    if attack:
        distribution = [0.2,0.2,0.6]
    else:
        distribution = [0.8,0.1,0.1]
    
    data = get_data_helper()
    while(data == ""):
        time.sleep(50)
        data = get_data_helper()
    f = open(filename, 'ab+')
    data_chunks = [data[i:i+writes_size] for i in range(0, len(data), writes_size)]    
    
    for chunk in data_chunks:

        if(len(chunk) < writes_size):
            continue

        cur_mode = random.choices(modes,distribution)[0]
        if(cur_mode == 'encryption'):
            encrypted_chunk = encrypt_data(chunk, writes_size, password)
            f.write(encrypted_chunk + b'[[e]]')
        
        elif(cur_mode == 'normal'):
            f.write(chunk+b'[[ne]]')
        
        elif(cur_mode == 'mixed'):
            partition_size = random.choice(range(128,writes_size,128))
            chnk1 = chunk[0:partition_size]
            chnk2 = chunk[partition_size::]

            if(random.choice([True, False])):
                encrypted_chunk = encrypt_data(chnk1, partition_size, password)
                f.write(encrypted_chunk + chnk2 + b'[[mx]]')
            else:
                encrypted_chunk = encrypt_data(chnk2, writes_size - partition_size, password)
                f.write(chnk1 + encrypted_chunk + b'[[mx]]')
    f.close()

        
if __name__ == "__main__":
    time_to_run = float(input("How long should I at least run for? (in minutes) ")) * 60
    print("Default params are attack = False, chunk size = 4KB, Output file name = data.txt")
    default = input("run default? (y/n) ")

    if(default[0].lower() == 'y'):
        start = time.time()
        while(time.time() - start < time_to_run):
            print(f"\rrunning: {round((time.time()-start)/time_to_run, 2)*100}%" , end=' ')
            write_file()
        print("\nCompleted!")
    else:
        atk_switch = 'n'
        attack = input("Simulate attack? (y/n) ").lower()
        sz = input("""Chunk sizes in KB:
        (input rand for random sizes (4, 8, 16, 32) or blank for default) """)
        fname = input("Output file name: (leave blank for default) ").strip()
        if(attack[0].lower() == 'y'):
            atk = True
        else:
            atk = False
            atk_switch = input("would you like to switch for an attack after a time? ").strip().lower()
            if(atk_switch[0] == 'y'):
                attack_switch_time = float(input("After how long should we start an attack? "))*60
                while(attack_switch_time > time_to_run):
                    attack_switch_time = float(input("Your time to switch is greater than your time to run input a smaller one: "))
        
        rand = False
        if(sz.strip().isnumeric()):
            size = int(sz)
        elif(len(sz) > 0 and sz[0].lower() == 'r'):
            size = 0
            rand = True
        else:
            size = 4
            print("size set to default, rerun and enter just a number if you want to set size")

        if fname == '':
            fname = "data.txt"
        
        start = time.time()
        while(time.time() - start < time_to_run):
            if(atk_switch[0] == 'y' and time.time()-start > attack_switch_time and atk == False):
                print("\rSwitching to attack now!\t\t\t ")
                atk = True
            print(f"\rrunning: {round((time.time()-start)/time_to_run, 2)*100}%" , end=' ')
            if rand:
                size = random.choice([4,8,16,32])
            write_file(attack=atk,writes_size=size,filename=fname)
        print("\nCompleted!")
