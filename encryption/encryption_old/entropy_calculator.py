# This is a script which reads a file and continuously finds the entropy then outputs one number at the end

import collections
import math
import sys
import os
import time
import sqlite3
#------------------------------DataBase----------------------------------------------#
conn = sqlite3.connect('MLData.db')
c = conn.cursor()

#Create table - Encryption
try:
    c.execute('''CREATE TABLE ENCRYPTION
             (data TEXT, timestamp FLOAT, entropy FLOAT,buffer_size INT)''')
except:
    print("Encryption Table is Already Active.")
try:
    c.execute('''CREATE TABLE NETWORK
                 (data TEXT, timestamp FLOAT, URL TEXT, malicious TEXT)''')
except:
    print("Network Table is Already Active.")




#------------------------------------------------------------------------------------#

#------------------This is the entropy calculation Function---------------------------#
def calc_entropy(chunk, dataT,dataB,timeS):
    charProb = []
    chunky = dataB
    #All chunky used to be chunk
    if len(chunky) != 0:
        for b in range(256):
            ch = 0
            for byte in chunky:
                if byte == b:
                #if ord(byte) == b:
                    ch+=1
            charProb.append(float(ch)/len(chunky))
        entropy = 0.0
        totalProb = 0.0
        for prob in charProb:
            if prob > 0:
                totalProb += prob
                entropy = entropy + (prob * math.log(prob,2))
        entropy = entropy * -1
        #print("Entropy of chunk: ", entropy)
        #t = time.time()
        #time_stamp = time.ctime(t)

        t = timeS
        #print(timeS)
        #time_stamp = timeS
        c.execute("INSERT INTO ENCRYPTION (data, timestamp, entropy, buffer_size) values (?,?,?,4)",
                  (dataT, t, entropy))
        conn.commit()
        #print("insertion done")

#-----------------------------File Opener------------------------------------#
# First we check for the option of giving a filename
if len(sys.argv) != 2:
    print("No File Provided: will be attempting calculation on data.txt\n")
    fileName = "data.txt"
else:
    fileName = sys.argv[1]

# Now we will try to open and read using try/except
try:
    if fileName != "print_data":
        f = open(fileName, "rt+")
except:
    print("The file provided does not exist in this directory or can not be opened")

if len(sys.argv) >= 2:
    if len(sys.argv) > 2:
        if sys.argv[2] == "print_data" or sys.argv[1] == "print_data":
            DBdata = c.execute("SELECT data, timestamp, entropy, buffer_size FROM ENCRYPTION").fetchall()
            print(DBdata)
            sys.exit()
    else:
        if sys.argv[1] == "print_data":
            DBdata = c.execute("SELECT data, timestamp, entropy, buffer_size FROM ENCRYPTION").fetchall()
            print(DBdata)
            sys.exit()

#----------------------------------------------------------------------------#
# Once we open the file open we want to continuosly read in from the file
window = ""
pos = 0
window_type = 0
#---------------------------Constant Loop Monitor-----------------------------#
i = 0.1
timeS = 0.0
while True:
    #f = open(fileName,encoding="utf-8",errors='ignore')

    f = open(fileName,"rb+")
    f.seek(pos)
    byte_line = f.readline(4096)
    curr_line = byte_line.decode('utf-8','ignore')

    if curr_line == "":
        #print("End of File at pos: ", pos)

        rows = c.execute("SELECT data, timestamp, entropy, buffer_size FROM ENCRYPTION").fetchall()
        for r in rows:
            print(r)
        conn.close()
        time.sleep(36000)

    else:
        # -----------Pattern Creation---------------------------
        timeD = 0.1 * math.sin(i)

        if timeD <= 0.0:
            while timeD <= 0.0:
                i += 0.1
                timeD = 0.1 * math.sin(i)

        timeS = timeD + timeS
        #print("From reading:", timeS)
        # ------------------------------------------------------

        pos = f.tell()
        if curr_line.find("[[e]]") != -1:
            i+= 0.1
            #print("This is encrypted chunk!")
            #--------------------------------

            parseArr = curr_line.split("[[e]]")
            wantedChunk = parseArr[0]
            if len(parseArr) != 1:
                nextChunk = parseArr[1]
                window = window + wantedChunk
                calc_entropy(window, "E", byte_line,timeS)
                window = ""
            else:
                window = window + wantedChunk
                calc_entropy(window, "E", byte_line,timeS)
                window = nextChunk
                curr_line = nextChunk

        if curr_line.find("[[ne]]") != -1:
            i += 0.1
            #print("This is unencrypted chunk!")
            parseArr = curr_line.split("[[ne]]")
            wantedChunk = parseArr[0]
            if len(parseArr) != 1:
                nextChunk = parseArr[1]
                window = window + wantedChunk
                calc_entropy(window, "NE", byte_line,timeS)
                window = ""
            else:
                window = window + wantedChunk
                calc_entropy(window,"NE", byte_line,timeS)
                window = nextChunk
                curr_line = nextChunk

        if curr_line.find("[[mx]]") != -1:
            i += 0.1
            #print("This is unencrypted chunk!")
            parseArr = curr_line.split("[[ne]]")
            wantedChunk = parseArr[0]
            if len(parseArr) != 1:
                nextChunk = parseArr[1]
                window = window + wantedChunk
                calc_entropy(window, "MX", byte_line,timeS)
                window = ""
            else:
                window = window + wantedChunk
                calc_entropy(window, "MX", byte_line,timeS)
                window = nextChunk
                curr_line = nextChunk
        else:
            timeS = timeS - timeD
            continue
            #print("No flags for current chunk")
        window = window + curr_line[:-1]    #We use :-1 to exclude the new line char, but this might be needed
    
    f.close()

