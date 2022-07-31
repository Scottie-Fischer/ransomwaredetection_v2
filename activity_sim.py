from math import ceil
import time
import random
from encryption import populate_file


def write_net_data(n_filename, url_list):
    n_outfile = open(n_filename, 'a+')
    
    url = random.choice(url_list)
    
    n_outfile.write(url)
    n_outfile.close()






if __name__ == '__main__':
    switch_time = 0

    run_default = (input('Run default? (y/n) ') == 'y')
    if run_default:
        d_filename = 'encryption/mem_data.txt'
        n_filename = 'network/net_data.txt'
        n_good_filepath = 'network/good_urls.txt'
        n_bad_filepath = 'network/bad_urls.txt'
        
    else:
        d_filename = input("Data Filename: ").strip()
        n_filename = input("Network output filename: ").strip()
        n_good_filepath = input("Good network file path: ").strip()
        n_bad_filepath = input("Bad network file path: ").strip()
    
    time_to_run = float(input("time to run: ").strip())*60
    attack_switch = (input('Attack switch? (y/n) ').strip() == 'y')
    if(attack_switch):
        switch_time = float(input("switch time: ").strip())*60
        

    url_list = open(n_good_filepath, 'r+').readlines()
    bad_file = open(n_bad_filepath, 'r+')

    attack = False
    start = time.time()

    while(time.time()-start < time_to_run):
        print(f"\rrunning: {ceil(((time.time()-start)/time_to_run)*100)}%" , end=' ')
        
        if(not attack and attack_switch and time.time() - start > switch_time):
            print(f"\rSwitching to attack at", time.strftime("%H:%M:%S",time.localtime()), "\t\t\t")
            attack = True
            bad_urls = bad_file.readlines()
            write_net_data(n_filename, bad_urls)
            url_list.extend(bad_urls)
        
        populate_file.write_file(attack=attack, filename=d_filename)
        write_net_data(n_filename,url_list)

    print("Complete!")