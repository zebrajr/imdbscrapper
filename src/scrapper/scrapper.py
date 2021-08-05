import os
import time
from time import sleep
import datetime
import json
import requests
import csv
import logging
import mysql.connector as mariadb
from multiprocessing import Process
from bs4 import BeautifulSoup
import rsc.functions as scrapper
import rsc.helper as helper



def main():
    helper.cls()

    #imdbscrapper(903747,903733)


    remDuplicates       = int(os.getenv('removeDuplicates', 0))     # If 1: call removeDuplicates()
    nrProcesses         = int(os.getenv('PROCESSES', 5))            # Number of Processes to start in parallel
    startURL            = int(os.getenv('START_URL', 10000000))     # Starting Number
    endURL              = int(os.getenv('END_URL', 0))              # Ending Number
    stepUpCycle         = int(os.getenv('STEPUPCYCLE', 100))        # How many numbers will be checked in each cycle
    stepUpProcess       = int(stepUpCycle / nrProcesses)    # Divides the numbers to be checked in each cycle by the total number of processes
                                                        # Eg: 5 Processes running each cycle. 100 Numbers each cycle. 20 Numbers per process

    # Remove Duplicates on boot?
    if remDuplicates == 1:
        scrapper.removeDuplicates()

    # Parses the Starting and ending values to temp variables as to keep track
    # [ToDo] it might be unnecessary?
    currentStartURL = startURL
    currentEndURL   = startURL - stepUpProcess
    # Execute until endURL is reached
    while currentEndURL > endURL:
        # Initializes a list to old the processes
        processes = []
        # For each process, calculate the starting and ending number, and start a process with those values
        for i in range(nrProcesses):
            print("%s :: Process: %s - Starting: %s - Ending: %s" % (datetime.datetime.now(), i, currentStartURL, currentEndURL))
            if(currentEndURL < endURL):
                currentEndURL = endURL
            processes.append(Process(target=scrapper.imdbscrapper,args=(currentStartURL, currentEndURL)))
            currentStartURL -= stepUpProcess
            currentEndURL   -= stepUpProcess

        for process in processes:
            process.start()

        for process in processes:
            process.join()



if __name__ == "__main__":
    main()
