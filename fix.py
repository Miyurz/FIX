import sys
import os
import time
import time
import datetime
import matplotlib
import pandas as pd
from collections import Counter

fileName = "cme-msg-trace-cl-CME-2016-04-14T21_24_48.086Z.db"

def downloadRecentFixFile(hostname, username,port, password):
    global fileName
    fileName = "cme-msg-trace-cl-CME-2016-04-14T21_24_48.086Z.db" 
    # mykey = paramiko.RSAKey.from_private_key_file('~/My-ssh.priv')  # This is when password less login is setup
    password = password                                             # This is used when password is used to login      
    host = hostname
    username = username
    port = port

    transport = paramiko.Transport((host, port))
    
    transport.connect(username = username, password = password) # This is used when password is used to login
    
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir('outgoing')

    for fileattr in sftp.listdir_attr():
        try:
            if fileattr.filename.startswith('cme-msg') and fileattr.st_mtime > latest:
                latest = fileattr.st_mtime
                latestfile = fileattr.filename
                print "Downloading file ==> " + latestfile
                sftp.get(filename, localpath)
        except IOError as e:
            print e
    sftp.close()
    transport.close()

    for filename in sftp.listdir():
        try:
            if filename.startswith('cme-msg-trace-cl-CME-%s.csv'%formattedtime):
                localpath= destination + '/' + filename
                print "Downloading files ==> " + filename
                sftp.get(filename, localpath)   
        except IOError as e:
            print e
    sftp.close()
    transport.close()


def calculateOrderSingle():
    #print(inspect.currentframe().f_code.co_name)
    SOH='\x01'
    NEWLINE="\n"
    DELIMITER='='
    SENDING_TIME_TAG="52"
    x = []
    y = []
    time_slot = open('time_slot.txt', 'w') 
    with open(fileName) as FileObj:
        for line in FileObj:
            #print("New line is"+line)
            line = line.strip("\n").split(SOH)
            #print ("Sanitised line is "+str(line))
            #print "Number of items in line="+str(len(line))
            tag = ""
            value = ""
            for pair in line:
                if pair is not "":
                    #print("pair is "+pair)
                    #print pair.split(DELIMITER)
                    tag =  pair.split(DELIMITER)[0]
                    value = pair.split(DELIMITER) [1]
                    #print("tag is "+tag)
                    #print("value is "+value)
                    if tag == SENDING_TIME_TAG:
                        #print("value = "+value)
                        myDate = value.replace("-", " ")
                        #20160415-02:02:08.678
                        #print myDate
                        dt_obj = datetime.datetime.strptime(myDate,"%Y%m%d %H:%M:%S.%f")
                        dt_str = datetime.datetime.strftime(dt_obj,"%Y-%m-%d %H:%M:%S")
                        #print dt_str

                        #dt = time.mktime(dt.timetuple()) + (dt.microsecond / 1000000.0)
                        #dt = time.mktime(dt.timetuple())
                        x.append(dt_str)
                        #y.append(myDate)
                        #print>>time_slot,("{0:.3f}".format(tmp))
                        #print>>time_slot, tmp

    #print("Number of items = "+str(len(x)))
    d = Counter(x)
    n, m = d.keys(), d.values()
    #print n, m
    #print("Number of items in keys = "+str(len(n)))
    #print("Number of items in values = "+str(len(m)))
    #for f, b in zip(n, m):
        #print "key = %.1f value = %.1f" % (f, b)
        #print "{} Order single message(s) sent at  timestamp {}".format(b,f)
    #return n,m
    #printStats(m,n)
    plotData(n,m)
    #frequency_msg = open('frequency_msg.txt', 'w')
    #print>>frequency_msg,dict((X,x.count(X)) for X in set(x))
    #time.sleep(0)
    #print("\n")

def printStats(list1, list2):
    print list1
    print list2
    #print set(list2)
    #print set(list1)

def plotData(list1, list2):
    import matplotlib.pyplot as plt 
    import matplotlib.dates as mdates
    import datetime as dt
    import dateutil
    print list1
    print list2

    x = [dt.datetime.strptime(d,'%Y-%m-%d %H:%M:%S').date() for d in list1]
    #x = [datetime.datetime.strptime('{:08}'.format(int(date)),'%Y%m%d %H:%M:%S') for date in list1]
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    plt.plot(x, list2)
    plt.gcf().autofmt_xdate()

    #dates = matplotlib.dates.date2num(list1)
    #print dates
    #matplotlib.pyplot.plot_date(dates, list2)
    
    #plt.scatter(list1, list2)
    #dates = [pd.to_datetime(d) for d in list1]
    #print dates
    #print list2
    #plt.scatter(dates, list2, s =100, c = 'red')
    plt.title('Plotting graph between time stamp and message rate')
    plt.xlabel('Timestamp')
    plt.ylabel('Message rate')
    #plt.xlim(0,5)
    #plt.ylim(0,100000)
    plt.show()


downloadRecentFixFile()
calculateOrderSingle()
#list1, list2 = calculateOrderSingle()
