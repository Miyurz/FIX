import sys
import paramiko
import os
import time
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import datetime
import dateutil
import numpy as np

fileName = ""

def downloadRecentFixFile():
    global fileName

    #Export these variables.
    password = os.environ.get('ftp_password')                                    
    host = os.environ.get('ftp_host')                                                   
    username = os.environ.get('ftp_username')                             
    port = 22 
    
    #password = "password" 
    #host = "test.rebex.net"
    #username = "demo"                           
    
    paramiko.util.log_to_file("paramiko.log")
    try:

        transport = paramiko.Transport((host, port))
        transport.connect(username = username, password = password)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    else:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir('/data/sample')
    finally:
        print "Cleaning up the stuff before leaving try"
    
    '''
         Sample FTP server list: Contents of artefacts directory on ftp server
         -rwxr-xr-x  1 mnagekar  admins  2397869 Dec  2 17:42 cme-msg-trace-cl-CME-2016-04-14T21_24_48.086Z.db
         -rwxr-xr-x  1 mnagekar  admins  2397869 Dec  2 16:12 cme-msg-trace-cl-CME-2016-04-14T21_24_48.087Z.db
         -rwxr-xr-x  1 mnagekar  admins  2397869 Dec  2 16:15 cme-msg-trace-cl-CME-2016-04-14T21_24_48.088Z.db
         -rwxr-xr-x  1 mnagekar  admins  2397869 Dec  2 16:18 cme-msg-trace-cl-CME-2016-04-14T21_24_48.089Z.db
         -rwxr-xr-x  1 mnagekar  admins  2397869 Dec  2 16:19 cme-msg-trace-cl-CME-2016-04-14T21_24_48.090Z.db

    '''

    latest = 0
    latestfile = None
    
    for fileattr in sftp.listdir_attr():
        try:
            if fileattr.filename.startswith('cme-msg') and fileattr.st_mtime > latest:
                latest = fileattr.st_mtime
                latestfile = fileattr.filename
                print latestfile
        except IOError as e:
            print e
    
    if latestfile is not None:
        fileName = latestfile
        print "Downloading file ==> " + fileName
        sftp.get(fileName, fileName)
    else:
        print "ERROR: Didn't find the file to download"
        sys.exit(1)
    
    sftp.close()
    transport.close()

def calculateOrderSingle():
    
    SOH='\x01'
    NEWLINE="\n"
    DELIMITER='='
    SENDING_TIME_TAG="52"
    msgTimestamp = []
    time_slot = open('time_slot.txt', 'w') 
    
    with open(fileName) as FileObj:
        for line in FileObj:
            line = line.strip("\n").split(SOH)
            tag = ""
            value = ""
            for pair in line:
                if pair is not "":
                    tag =  pair.split(DELIMITER)[0]
                    value = pair.split(DELIMITER) [1]
                    if tag == SENDING_TIME_TAG:
                        myDate = value.replace("-", " ")
                        #20160415-02:02:08.678
                        dt_obj = datetime.datetime.strptime(myDate,"%Y%m%d %H:%M:%S.%f")
                        dt_str = datetime.datetime.strftime(dt_obj,"%Y-%m-%d %H:%M:%S")

                        #dt = time.mktime(dt.timetuple()) + (dt.microsecond / 1000000.0)
                        msgTimestamp.append(dt_str)

    keyValue = Counter(msgTimestamp)
    n, m = keyValue.keys(), keyValue.values()
    for f, b in zip(n, m):
        print "{} Order single message(s) sent at  timestamp {}".format(b,f)
    printStats(n,m)
    plotData(n,m)
    
    #frequency_msg = open('frequency_msg.txt', 'w')
    #print>>frequency_msg,dict((X,x.count(X)) for X in set(x))

def printStats(x, y):
    
    print("Median for message rate => {} ".format(np.median(y)))
    
    print("99 percentile => {} ".format(np.percentile(y, 99)))
    
    print("Max => {} ".format(np.max(y)))
    
    print("Min => {}".format(np.min(y)))

def plotData(x, y):

    x1 = [datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S').date() for d in x]
    
    plt.title('Plotting graph between time stamp and message rate')
    plt.xlabel('Timestamp')
    plt.ylabel('Message rate')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    
    plt.plot(x1, y)
    plt.gcf().autofmt_xdate()
    
    plt.show()

if __name__ == '__main__':
    downloadRecentFixFile()
    calculateOrderSingle()
