import os
import time
import datetime
import json
import requests
import csv
import logging
import mysql.connector as mariadb
from multiprocessing import Process
from bs4 import BeautifulSoup

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

'''
    Function to save data from lists (eg: movieTable) to file (eg: moviesFile)
'''
def saveToFile(dataTable, dataPath):
    # Assume we couldn't open / write to file
    sucessTest = False
    while sucessTest != True:
        # Try to open the file and append to it
        # [ToDo:] change try position to fix duplicate entries
        try:
            f = open(dataPath, "a")
            for row in dataTable:
                # Initialize an empty Output String
                outputStr = ""
                # For each value in the list, add it as string to the output, separate each by ";"
                for index, value in enumerate(row):
                    outputStr += str(value) + ";"
                # Adds the new line (\n) to the string, writes to the file, prints to the screen
                outputStr += "\n"
                f.write(outputStr)
                print(row)
            f.close()
            # If sucess, then file can move on
            sucessTest = True
        except Exception as e:
            print("Retrying updating - %s - %s" % (dataPath, e))

def checkForDuplicate(idCheck):
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)
    # [TODO] Should be changed to one procedure call only
    cursor.callproc('checkDuplicateMovie', [idCheck,])
    for results in cursor.stored_results():
        result = results.fetchall()
    commitDBConnection(mydb)
    if len(result) > 0:
        return False


# Creates and returns a mariadb connection object
def createDBConnection():
    mydb = mariadb.connect(
        host = 'imdbdb',
        user = 'root',
        password = 'secret',
        database = 'imdbscrapper'
    )
    return mydb

def commitDBConnection(database):
    database.commit()
    database.close()


def saveToDatabase(dataTable, inTable):
    # [TODO] Change to dynamic values from docker-compose.yml
    mydb = createDBConnection()
    cursor = mydb.cursor(buffered=True)

    # row[0] idMovie
    # row[1] name
    # row[2] description
    # row[3] url
    # row[4] genres
    # row[5] rating
    # row[6] ratingCount
    # row[7] releaseDate


    # Defines which procedures to call
    if (inTable == 'movies'):
        mainTable = 'insertMovie'
        genreTable = 'insertMovieGenre'
    if (inTable == 'series'):
        mainTable = 'insertSerie'
        genreTable = 'insertSerieGenre'

    for row in dataTable:
        cursor.callproc(mainTable, [row[0],row[1],row[2],row[3],row[5],row[6],row[7],])
        try:
            if len(row[4]) > 1:
                for genre in row[4]:
                    cursor.callproc(genreTable, [row[0],genre,])
                continue
        except Exception as e:
            cursor.callproc(genreTable, [row[0],str(row[4]),])
    commitDBConnection(mydb)


'''
    Main Function for the scrapper
    It will prepare the URL, request it, get the answer, parse the information to a list,
        append that list to another list and finally call savetoFile(dataTable, dataPath)
        to save it to a file
    Requires a starting and an ending URL (in Int), going in decreasing order (eg: 1000, 999, 998, etc)
'''
def imdbscrapper(startURL, endURL):

    # Configuration values for the scrapper
    baseURL         = "https://www.imdb.com/title/tt"       # Base URL for each title
    debugLevel      = 40                                    # 20 will display Info messages, 40 errors
    #logFile         = "/opt/storage/info.log"               # Log output
    counterFile     = "/opt/storage/counter.txt"            # Which ID was last scanned
    reCheckFile     = "/opt/storage/recheck.txt"            # Which IDs to recheck
    moviesFile      = "/opt/storage/movies.csv"             # Where to store movie info
    seriesFile      = "/opt/storage/series.csv"             # Where to store shows/series info

    # Initialize List of lists
    movieTable   = []
    serieTable   = []
    errorTable   = []
    reCheckTable = []
    # Go in descending order from startURL to endURL
    for i in range(startURL, endURL, -1):
        #logging.basicConfig(filename=logFile, level=logging.INFO)
        titleFixed = str(i).zfill(7)               # Adds leading zeros, so that it always has 7 digits
        url        = baseURL + titleFixed + '/'    # String Joins every part of the URL
        dataRow    = []                            # Initializes the dataRow list
        errorRow   = []                            # Initializes the errorRow list
        reCheckRow = []                            # Initializes the reCheckRow list

        # Assume Non Duplicate
        duplicateTest = True
        # Test for Duplicate
        duplicateTest = checkForDuplicate(titleFixed)

        # If a duplicate is found, skip number
        if duplicateTest is False:
            continue
        try:
            dataRow.append(titleFixed)
            # Requests, parses and loads into JSON the HTML response
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            data = json.loads(soup.find('script', type='application/ld+json').string)

            # If the response is a TVEpisode, just skip the number altogether
            if(data['@type'] == 'TVEpisode'):
                continue

            # Gets the desired values from the JSON response
            dataRow.append(data['name'])
            try:
                dataRow.append(str(data['description']).replace(';', ''))
            except Exception as e:
                dataRow.append("Description unavailable")
            dataRow.append(url)
            try:
                dataRow.append(data['genre'])
            except Exception as e:
                dataRow.append(0)
            try:
                dataRow.append(data['aggregateRating']['ratingValue'])
            except Exception as e:
                dataRow.append(0)
            try:
                dataRow.append(data['aggregateRating']['ratingCount'])
            except Exception as e:
                dataRow.append(0)
            try:
                dataRow.append(data['datePublished'])
            except Exception as e:
                dataRow.append('1000-01-01')

            # Checks if its a movie or a serie/show, and append the list to the list of lists
            if(data['@type'] == 'Movie'):
                movieTable.append(dataRow)
            if(data['@type'] == 'TVSeries'):
                serieTable.append(dataRow)
        except Exception as e:
            # Prepares the error string, then append the error list to the list of lists of errors
            errorMessage = titleFixed + " - " + str(e)
            errorRow.append(errorMessage)
            errorTable.append(errorRow)
            # If the error is page not available, append to reCheck list (Performance improvement on rechecks)
            if("NoneType" in str(e)):
                recheckString = titleFixed + "\n"
                reCheckRow.append(recheckString)
                reCheckTable.append(reCheckRow)
    # Writes the list of lists to each correct file
    #saveToFile(movieTable, moviesFile)
    #saveToFile(serieTable, seriesFile)
    #saveToFile(errorTable, logFile)
    #saveToFile(reCheckTable, reCheckFile)
    saveToDatabase(movieTable, 'movies')
    saveToDatabase(serieTable, 'series')

def main():
    cls()

    #imdbscrapper(903747,903743)

    nrProcesses     = int(os.getenv('PROCESSES', 5))         # Number of Processes to start in parallel
    startURL        = int(os.getenv('START_URL', 10000000))  # Starting Number
    endURL          = int(os.getenv('END_URL', 0))           # Ending Number
    stepUpCycle     = int(os.getenv('STEPUPCYCLE', 100))     # How many numbers will be checked in each cycle
    stepUpProcess   = int(stepUpCycle / nrProcesses)    # Divides the numbers to be checked in each cycle by the total number of processes
                                                        # Eg: 5 Processes running each cycle. 100 Numbers each cycle. 20 Numbers per process

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
            processes.append(Process(target=imdbscrapper,args=(currentStartURL, currentEndURL)))
            currentStartURL -= stepUpProcess
            currentEndURL   -= stepUpProcess

        for process in processes:
            process.start()

        for process in processes:
            process.join()



if __name__ == "__main__":
    main()
