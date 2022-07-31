import threading
import time

from encryption import encryption_calculation
from encryption import moving_window
from network import network_classification



def entropy_alert(network_flag):
    print("flag in thread:", network_flag)
    if network_flag:
        print("alert at ", time.strftime("%H:%M:%S",time.localtime()))
    else:
        print("Adjusting for seasonality")

def entropy_t_func(fileName, db_fileName):
    encryption_calculation.entropy_to_db(fileName,db_filename=db_fileName, running_msg_flag=False)

def moving_window_t_func(dbFileName, network_flag, startDelay=900):
    time.sleep(startDelay)
    moving_window.moving_window(dbFileName, startDelay, network_flag)

def net_t_func(network_filename, db_filename, network_ml_model_filename):
    network_classification.main(fileName=network_filename, db_fileName=db_filename, model_fileName=network_ml_model_filename)

if __name__ == '__main__':
    data_fileName = "encryption/mem_data.txt"
    db_filename = 'maliciousness.db'
    network_filename = 'network/net_data.txt'
    network_ml_model_filename = 'network/model.pkl'
    network_flag = threading.Event()

    entropy_thread = threading.Thread(target=entropy_t_func, args=(data_fileName,db_filename))
    entropy_thread.start()

    moving_window_thread = threading.Thread(target=moving_window_t_func, args=(db_filename, network_flag,))
    moving_window_thread.start()

    network_classif_thread = threading.Thread(target=net_t_func, args=(network_filename, db_filename, network_ml_model_filename,))
    network_classif_thread.start()

    time.sleep(30)
    while True:
        if not network_flag.is_set(): 
            if network_classification.check_db_for_malicious_conn(db_filename):
                network_flag.set()
            else:
                time.sleep(60)
        else:
            time.sleep(900)
            network_flag.clear()
